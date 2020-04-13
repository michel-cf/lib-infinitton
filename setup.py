from distutils.core import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='libinfinitton',
    packages=['.'],
    version='0.3',
    license='MIT',
    description='Cross platform library to use Infinitton device',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Michel Lampo',
    author_email='michel.lampo@creatingfuture.eu',
    url='https://github.com/michel-cf/lib-infinitton',
    keywords=['INFINITTON', 'USB-HID', 'KEYWORDS'],
    install_requires=[
        'hid',
        'Pillow',
        'PyEventEmitter',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Typing :: Typed'
    ],
    python_requires='>=3.6',
)
