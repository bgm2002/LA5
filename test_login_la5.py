import os
import sys
import argparse
import importlib.util
import types

# Preparar paquete simulado para soportar imports relativos de api.py
BASE = os.path.join('custom_components', 'fusion_solar_app')

pkg_cc = types.ModuleType('custom_components')
pkg_cc.__path__ = [os.path.abspath('custom_components')]
sys.modules['custom_components'] = pkg_cc

pkg = types.ModuleType('custom_components.fusion_solar_app')
pkg.__path__ = [os.path.abspath(BASE)]
sys.modules['custom_components.fusion_solar_app'] = pkg

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

const = load_module('custom_components.fusion_solar_app.const', os.path.join(BASE, 'const.py'))
utils = load_module('custom_components.fusion_solar_app.utils', os.path.join(BASE, 'utils.py'))
fs_api = load_module('custom_components.fusion_solar_app.api', os.path.join(BASE, 'api.py'))

parser = argparse.ArgumentParser()
parser.add_argument('--user', required=False, default=os.environ.get('FS_USER'))
parser.add_argument('--password', required=False, default=os.environ.get('FS_PASS'))
parser.add_argument('--host', required=False, default=os.environ.get('FS_HOST', 'la5.fusionsolar.huawei.com'))
parser.add_argument('--captcha', required=False, default=os.environ.get('FS_CAPTCHA', ''))
parser.add_argument('--data-host', dest='data_host', required=False, default=os.environ.get('FS_DATA_HOST'))
parser.add_argument('--dp-session', dest='dp_session', required=False, default=os.environ.get('FS_DP_SESSION'))
args = parser.parse_args()

def main():
    assert args.user and args.password, 'Defina --user y --password (o FS_USER/FS_PASS)'
    api = fs_api.FusionSolarAPI(
        args.user,
        args.password,
        args.host,
        args.captcha,
        data_host=args.data_host,
        dp_session=args.dp_session,
    )
    try:
        ok = api.login()
        print('login_ok=', ok, 'connected=', api.connected, 'data_host=', api.data_host)
        devices = api.get_devices()
        print('devices=', len(devices))
        for d in devices[:5]:
            print(d.device_id, d.state)
    except fs_api.APIAuthCaptchaError:
        api.set_captcha_img()
        if api.captcha_img and api.captcha_img.startswith('data:image/png;base64,'):
            import base64
            b64 = api.captcha_img.split(',')[1]
            with open('captcha.png','wb') as f:
                f.write(base64.b64decode(b64))
            print('CAPTCHA_REQUIRED: Abra captcha.png y ejecute con FS_CAPTCHA=XXXX')
        else:
            print('CAPTCHA_REQUIRED: sin imagen')
    except fs_api.APIAuthError as e:
        print('LOGIN_FAILED:', e)

if __name__ == '__main__':
    main()


