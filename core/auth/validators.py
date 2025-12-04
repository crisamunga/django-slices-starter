from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class PasswordComplexityValidator:
    """
    Validate that the password is of a minimum length.
    """

    def __init__(
        self, min_uppercase: int = 1, min_lowercase: int = 1, min_digits: int = 1, min_special: int = 1
    ) -> None:
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special

    def validate(self, password: str, user: User | None = None) -> None:
        uppercase_count = sum(1 for c in password if c.isupper())
        lowercase_count = sum(1 for c in password if c.islower())
        digit_count = sum(1 for c in password if c.isdigit())
        special_count = sum(1 for c in password if not c.isalnum())

        errors = []
        if uppercase_count < self.min_uppercase:
            errors.append(
                ValidationError(
                    _("Password must contain at least %(min_uppercase)d uppercase letter(s).")
                    % {"min_uppercase": self.min_uppercase},
                    code="password_not_complex_enough",
                )
            )
        if lowercase_count < self.min_lowercase:
            errors.append(
                ValidationError(
                    _("Password must contain at least %(min_lowercase)d lowercase letter(s).")
                    % {"min_lowercase": self.min_lowercase},
                    code="password_not_complex_enough",
                )
            )
        if digit_count < self.min_digits:
            errors.append(
                ValidationError(
                    _("Password must contain at least %(min_digits)d digit(s).") % {"min_digits": self.min_digits},
                    code="password_not_complex_enough",
                )
            )
        if special_count < self.min_special:
            errors.append(
                ValidationError(
                    _("Password must contain at least %(min_special)d special character(s).")
                    % {"min_special": self.min_special},
                    code="password_not_complex_enough",
                )
            )

        if errors:
            raise ValidationError(errors, code="password_not_complex_enough")

    def get_help_text(self) -> str:
        return _(
            "Your password must contain at least %(min_uppercase)d uppercase letter(s), "
            "%(min_lowercase)d lowercase letter(s), "
            "%(min_digits)d digit(s), and "
            "%(min_special)d special character(s)."
        ) % {
            "min_uppercase": self.min_uppercase,
            "min_lowercase": self.min_lowercase,
            "min_digits": self.min_digits,
            "min_special": self.min_special,
        }
