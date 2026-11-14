import logging


def test_webhook_cli_supports_once_and_watch_modes(app, monkeypatch):
    calls = []
    def deliver(limit):
        calls.append(limit)
        return {'attempted': 0, 'delivered': 0, 'failed': 0, 'skipped': 0}
    monkeypatch.setattr('app.services.developer.webhook_worker.deliver', deliver)
    runner = app.test_cli_runner()
    result = runner.invoke(args=['deliver-webhooks', '--limit', '3'])
    assert result.exit_code == 0 and 'attempted: 0' in result.output
    def stop(seconds):
        assert seconds == 2
        raise KeyboardInterrupt()
    monkeypatch.setattr('app.services.developer.webhook_worker.time.sleep', stop)
    result = runner.invoke(args=['deliver-webhooks', '--watch', '--interval', '2', '--limit', '4'])
    assert result.exit_code == 0 and 'worker stopped' in result.output
    assert calls == [3, 4]


def test_worker_failure_never_logs_exception_secrets(app, monkeypatch, caplog):
    def fail(limit):
        raise RuntimeError('SECRET-MUST-NOT-APPEAR')
    monkeypatch.setattr('app.services.developer.webhook_worker.deliver', fail)
    with caplog.at_level(logging.ERROR):
        result = app.test_cli_runner().invoke(args=['deliver-webhooks'])
    assert result.exit_code != 0
    assert 'RuntimeError' in caplog.text
    assert 'SECRET-MUST-NOT-APPEAR' not in caplog.text + result.output
