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
    # time.sleep(.005)
    # infinitton.fill_color(0, 255, 0, 0)

    infinitton.fill_image_path(0, 'folder.png')

    # for key in range(NUM_KEYS):
    #    infinitton.fill_color(key, COLOR_VALUES[int(key / 5)], COLOR_VALUES[int(key % 5)], COLOR_VALUES[key % 5])
    #    time.sleep(.005)

    time.sleep(60)

    infinitton.disconnect()
