"""Compatibility name for the existing OTP challenge model."""
from app.models.login_code import LoginCode

EmailOtpChallenge = LoginCode
