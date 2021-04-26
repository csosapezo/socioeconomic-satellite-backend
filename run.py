import argparse

from app import create_app

parser = argparse.ArgumentParser()
arg = parser.add_argument
arg('--mode', type=str, default='DEVELOPMENT', help='API start mode')

args = parser.parse_args()

app = create_app(args.mode)

if __name__ == '__main__':
	app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
