import math

def calculate_shake(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
    """
    Computes shake magnitude using a basic root sum square method.
    """
    accel_magnitude = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
    gyro_magnitude = math.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2)
    return accel_magnitude + gyro_magnitude



