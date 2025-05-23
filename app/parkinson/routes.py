from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from statistics import mean

from app.models.models import db, ParkinsonMetric, User, MedicationLog
from app.utils.shake_analysis import calculate_shake
import os
from tensorflow.keras.models import load_model
from app.utils.progress_lstm import train_lstm_model, build_lstm_data, MODEL_DIR

parkinson_bp = Blueprint('parkinson', __name__, url_prefix='/parkinson')


@parkinson_bp.route('/log', methods=['POST'])
def log_shake_data():
    data = request.get_json()
    required_fields = ['user_id', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    user_id = data['user_id']

    try:
        shake = calculate_shake(
            data['accel_x'], data['accel_y'], data['accel_z'],
            data['gyro_x'], data['gyro_y'], data['gyro_z']
        )

        metric = ParkinsonMetric(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            shake_per_minute=shake
        )
        db.session.add(metric)
        db.session.commit()

        return jsonify(metric.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@parkinson_bp.route('/<user_id>/shake-by-minute', methods=['GET'])
def get_shake_by_minute(user_id):
    day_str = request.args.get('day')  # expected format: YYYY-MM-DD
    if not day_str:
        return jsonify({'error': 'Missing "day" query parameter'}), 400

    try:
        day = datetime.strptime(day_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    next_day = day + timedelta(days=1)

    metrics = (
        ParkinsonMetric.query
        .filter(ParkinsonMetric.user_id == user_id,
                ParkinsonMetric.timestamp >= day,
                ParkinsonMetric.timestamp < next_day)
        .order_by(ParkinsonMetric.timestamp)
        .all()
    )

    results = {}
    for m in metrics:
        key = m.timestamp.strftime("%H:%M")
        results.setdefault(key, []).append(m.shake_per_minute)

    summarized = {k: sum(v) / len(v) for k, v in results.items()}
    return jsonify(summarized)


@parkinson_bp.route('/<user_id>/medication-effect', methods=['GET'])
def analyze_medication_effect(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    meds = user.get_medicamente()
    metrics = ParkinsonMetric.query.filter_by(user_id=user_id).all()

    timeline = {}
    for m in metrics:
        date = m.timestamp.date().isoformat()
        timeline.setdefault(date, []).append(m.shake_per_minute)

    analysis = {
        date: sum(vals) / len(vals)
        for date, vals in timeline.items()
    }

    return jsonify({
        "medications": meds,
        "daily_shake_avg": analysis
    })


@parkinson_bp.route('/<user_id>/log-medication', methods=['POST'])
def log_medication(user_id):
    """
    Log the time the user actually took medication.
    Optional: pass timestamp (ISO format), else defaults to now.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    timestamp_str = data.get("timestamp")

    try:
        med_time = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.utcnow()
    except ValueError:
        return jsonify({"error": "Invalid timestamp format. Use ISO 8601."}), 400

    log = MedicationLog(user_id=user_id, timestamp=med_time)
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "message": "Medication time logged successfully",
        "log": log.to_dict()
    }), 201


@parkinson_bp.route('/<user_id>/medication-response', methods=['GET'])
def medication_response(user_id):
    """
    Check if medication was effective after each intake.
    Compares 30 minutes before vs 90 minutes after medication log.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    logs = MedicationLog.query.filter_by(user_id=user_id).all()
    metrics = ParkinsonMetric.query.filter_by(user_id=user_id).all()

    response = []

    for log in logs:
        before = [
            m.shake_per_minute
            for m in metrics
            if log.timestamp - timedelta(minutes=30) <= m.timestamp < log.timestamp
        ]
        after = [
            m.shake_per_minute
            for m in metrics
            if log.timestamp <= m.timestamp < log.timestamp + timedelta(minutes=90)
        ]

        if before and after:
            before_avg = mean(before)
            after_avg = mean(after)
            response.append({
                "med_time": log.timestamp.isoformat(),
                "before_avg": round(before_avg, 2),
                "after_avg": round(after_avg, 2),
                "delta": round(before_avg - after_avg, 2),
                "effective": before_avg > after_avg
            })

    return jsonify({
        "medication_response": response
    })



@parkinson_bp.route('/<user_id>/train-progress-lstm', methods=['POST'])
def train_progress_lstm(user_id):
    """
    Train or retrain the LSTM model for “better” vs “worse” prediction.
    """
    if not User.query.get(user_id):
        return jsonify({'error': 'User not found'}), 404

    try:
        model_path = train_lstm_model(user_id)
        return jsonify({'message': 'LSTM model trained', 'model_path': model_path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@parkinson_bp.route('/<user_id>/predict-progress-lstm', methods=['GET'])
def predict_progress_lstm(user_id):
    """
    Predict if user is better or worse for a given date (YYYY-MM-DD), default today.
    """
    if not User.query.get(user_id):
        return jsonify({'error': 'User not found'}), 404

    # Determine target date
    date_str = request.args.get('date')
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str \
                      else datetime.utcnow().date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    # Build daily sequence data
    X, _ = build_lstm_data(user_id)
    if X is None:
        return jsonify({'error': 'Not enough data for prediction'}), 400

    # Load model file
    model_file = os.path.join(MODEL_DIR, f'progress_lstm_{user_id}.h5')
    if not os.path.exists(model_file):
        return jsonify({'error': 'Model not trained. Call /train-progress-lstm first.'}), 400
    model = load_model(model_file)

    # Map dates to sequence indices
    qs = ParkinsonMetric.query.filter_by(user_id=user_id) \
                              .order_by(ParkinsonMetric.timestamp).all()
    df = pd.DataFrame([{'date': m.timestamp.date(), 'shake': m.shake_per_minute}
                       for m in qs])
    daily = df.groupby('date').shake.mean().sort_index().reset_index()
    dates = list(daily.date.values)

    if target_date not in dates:
        return jsonify({'error': f'No data for {target_date}'}), 400
    idx = dates.index(target_date)
    timesteps = X.shape[1]
    if idx < timesteps:
        return jsonify({'error': 'Insufficient history for prediction'}), 400

    seq = daily.shake.values[idx-timesteps:idx].reshape(1, timesteps, 1)
    prob = float(model.predict(seq)[0][0])
    label = 'better' if prob >= 0.5 else 'worse'

    return jsonify({
        'date': target_date.isoformat(),
        'probability_better': prob,
        'prediction': label
    })