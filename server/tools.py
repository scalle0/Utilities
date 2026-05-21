from bridge import BridgeError, bridge

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "ping",
            "description": "Ping the STM32 microcontroller to check it is alive. Returns 'pong'.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "gpio_mode",
            "description": (
                "Configure a GPIO pin on the STM32. Call this once before reading "
                "or writing a pin. Pin 13 is the on-board user LED on most Arduino "
                "boards."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pin": {"type": "integer", "description": "Pin number, e.g. 13."},
                    "mode": {
                        "type": "string",
                        "enum": ["input", "input_pullup", "output"],
                    },
                },
                "required": ["pin", "mode"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "gpio_write",
            "description": (
                "Drive a GPIO pin HIGH (true) or LOW (false). The pin must already "
                "be configured as output via gpio_mode."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pin": {"type": "integer"},
                    "value": {"type": "boolean"},
                },
                "required": ["pin", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "gpio_read",
            "description": "Read the digital value of a GPIO pin. Returns 0 (LOW) or 1 (HIGH).",
            "parameters": {
                "type": "object",
                "properties": {"pin": {"type": "integer"}},
                "required": ["pin"],
            },
        },
    },
]

PARAM_ORDER = {
    "ping": [],
    "gpio_mode": ["pin", "mode"],
    "gpio_read": ["pin"],
    "gpio_write": ["pin", "value"],
}


async def dispatch(name: str, args: dict) -> object:
    if name not in PARAM_ORDER:
        raise BridgeError(f"unknown tool: {name}")
    positional = [args.get(k) for k in PARAM_ORDER[name]]
    return await bridge.call(name, positional)
