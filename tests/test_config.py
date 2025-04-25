from config import Config

config = Config('./tests/test_config.json')

def test_init():
    assert isinstance(config, Config)
    assert isinstance(config.getData(), dict)

def test_set():
    config.set('uwu', 'hi')
    assert config.get('uwu') == 'hi'

def test_nested():
    config.setNested("c", "a", "b")
    print(config._config_data)
    assert config.getNested("a") == {"b": "c"}

def test_save():
    data = config.getData()
    config.save()
    newConfig = Config('./tests/test_config.json')
    assert newConfig.getData() == data

def test_instance():
    config2 = Config('./tests/test_config.json')
    assert id(config2.getData()) == id(config.getData())