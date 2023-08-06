"""Use conversion methods to convert incoming QCells signals to correct physical values."""


def div10(val):
    """Divide value by 10."""
    return val / 10


def div100(val):
    """Divide value by 100."""
    return val / 100


INT16_MAX = 0x7FFF
INT32_MAX = 0x7FFFFFFF


def to_signed(val):
    """Decode unsigned signal to signed one. Encoding by 16bit."""
    if val > INT16_MAX:
        val -= 2**16
    return val


def to_signed32(val):
    """Decode unsigned signal to signed one. Encoding by 32bit."""
    if val > INT32_MAX:
        val -= 2**32
    return val


def twoway_div10(val):
    """Decode unsigned signal to signed one. Enoding by 16bit. Additionally divide by 10."""
    return to_signed(val) / 10


def twoway_div100(val):
    """Decode unsigned signal to signed one. Enoding by 16bit. Additionally divide by 100."""
    return to_signed(val) / 100


inverter_modes = {
    0: "Waiting",
    1: "Checking",
    2: "Normal",
    3: "Off",
    4: "Permanent Fault",
    5: "Updating",
    6: "EPS Check",
    7: "EPS Mode",
    8: "Self Test",
    9: "Idle",
    10: "Standby",
}


def get_intervter_mode(idx: int) -> str:
    """Translate inverter mode integer to descriptive string.

    :param idx: Inverter mode integer.
    """

    return inverter_modes.get(idx, "unknown inverter mode")


battery_modes = {
    0: "Self Use Mode",
    1: "Force Time Use",
    2: "Back Up Mode",
    3: "Feed-in Priority",
}


def get_battery_mode(idx: int) -> str:
    """Translate battery mode integer to descriptive string.

    :param idx: Battery mode integer.
    """
    return battery_modes.get(idx, "unknown battery mode")
