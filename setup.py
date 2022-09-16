from setuptools import setup, find_packages

requires = [
    'flask',
    'spotipy',
    'html5lib',
    'requests',
    'requests_html',
    'beautifulsoup4',
    'youtube_dl',
    'pathlib',
    'pandas'
]

setup(
    name='SpotifyToYoutubeMP3',
    version='1.0',
    description='An app that gets songs from your Spotify and downloads the YoutubeMP3 version',
    author='needmango',
    author_email='email@email.com',
    keywords="web flask",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires
)