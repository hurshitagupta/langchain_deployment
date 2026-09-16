from rollout.rollout import deploy, rollback


def test_successful_release():
    result = deploy(version="1.1.0",ready=True)
    assert result is True


def test_bad_release():
    result = deploy( version="1.1.0", ready=False)
    assert result is False


def test_rollback(capsys):
    rollback("1.0.0")

    output = capsys.readouterr().out

    assert "ROLLBACK" in output
    assert "1.0.0" in output