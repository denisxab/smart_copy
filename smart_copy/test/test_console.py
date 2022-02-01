from click.testing import CliRunner

from console import cli


def test_hello_world():
    runner = CliRunner()
    result = runner.invoke(cli, ['nameone', '-p', 'smart_copy.py', "helpful.py"])
    assert result.exit_code == 0
    assert result.output == 'Hello Peter!\n'


if __name__ == '__main__':
    test_hello_world()
