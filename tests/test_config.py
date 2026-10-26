import os
import subprocess
import sys


def run_config_with_env(overrides):
    """Run the configuration module in a fresh Python process."""
    env = os.environ.copy()
    env.update(overrides)

    # Prevent a developer's local .env from overriding test values.
    env["PYTHON_DOTENV_DISABLED"] = "1"

    return subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import app.core.config as c; "
                "print(c.APP_NAME); "
                "print(c.APP_ENV); "
                "print(c.APP_DEBUG); "
                "print(c.DEFAULT_LANGUAGE); "
                "print(','.join(c.SUPPORTED_LANGUAGES)"
                ")"
            ),
        ],
        env=env,
        capture_output=True,
        text=True,
    )


def test_valid_configuration_loads():
    result = run_config_with_env(
        {
            "APP_NAME": "Test_Chatbot",
            "APP_ENV": "testing",
            "APP_DEBUG": "true",
            "DEFAULT_LANGUAGE": "en",
            "SUPPORTED_LANGUAGES": "en,sw",
        }
    )

    assert result.returncode == 0, result.stderr
    assert "Test_Chatbot" in result.stdout
    assert "testing" in result.stdout
    assert "True" in result.stdout
    assert "en" in result.stdout
    assert "en,sw" in result.stdout


def test_invalid_default_language_is_rejected():
    result = run_config_with_env(
        {
            "APP_ENV": "testing",
            "DEFAULT_LANGUAGE": "fr",
            "SUPPORTED_LANGUAGES": "en,sw",
        }
    )

    assert result.returncode != 0
    assert "ValueError" in result.stderr
    assert "DEFAULT_LANGUAGE" in result.stderr


def test_invalid_environment_is_rejected():
    result = run_config_with_env(
        {
            "APP_ENV": "invalid",
            "DEFAULT_LANGUAGE": "en",
            "SUPPORTED_LANGUAGES": "en,sw",
        }
    )

    assert result.returncode != 0
    assert "ValueError" in result.stderr
    assert "APP_ENV" in result.stderr
