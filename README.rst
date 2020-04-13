.. image:: https://img.shields.io/pypi/v/libinfinitton.svg
    :target: https://pypi.org/project/libinfinitton

lib-infinitton
==============

Cross platform library to use `Infinitton screen keyboard <https://www.infinitton.com/>`__.


Install
-------

.. code-block:: console

     $ pip install libinfinitton

This uses a native library to connect to the usb port and at this time it is required that you
install this manually if it is not already present. The installation procedures for different operating systems
are shown on `pyhidapi github page <https://github.com/apmorton/pyhidapi>`__.

On linux it might be necessary to add the `53-infinitton.rules <setup/53-infinitton.rules>`__ to the
`/etc/udev/rules.d/` directory to avoid having to run as root.

Example
-------

.. code-block:: python

    #!/usr/bin/env python
    import libinfinitton
    import time


    if __name__ == "__main__":

        def down(button):
            print('down: %s' % button)


        def up(button):
            print('up: %s' % button)


        libinfinitton.Infinitton.is_present(0, 0)
        infinitton = libinfinitton.Infinitton()

        infinitton.on('down', down)
        infinitton.on('up', up)

        infinitton.clear_all_keys()
        # infinitton.fill_color(0, 255, 0, 0)

        infinitton.fill_image_path(0, 'folder.png')

        time.sleep(60)

        infinitton.disconnect()

In this example an icon is show on the first key (top-left). And for a duration of 60 seconds the keyboard will listen to key-presses.
On each press, at the time of down and up the key number is printed.

To view all available methods check the `documentation page <html/libinfinitton.html>`__.

License
-------

`libinfinitton` is released under the MIT license.

`libinfinitton is based on a nodejs based version. <https://github.com/bitfocus/node-elgato-stream-deck/tree/infinitton-idisplay>`__

The project owners are not affiliated with iDisplay Technology Co., Ltd, the creator of the Infinitton device.
