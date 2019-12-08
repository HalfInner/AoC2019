'''
--- Part Two ---
Now you're ready to decode the image. The image is rendered by stacking the layers and aligning the pixels with the same positions in each layer. The digits indicate the color of the corresponding pixel: 0 is black, 1 is white, and 2 is transparent.

The layers are rendered with the first layer in front and the last layer in back. So, if a given position has a transparent pixel in the first and second layers, a black pixel in the third layer, and a white pixel in the fourth layer, the final image would have a black pixel at that position.

For example, given an image 2 pixels wide and 2 pixels tall, the image data 0222112222120000 corresponds to the following image layers:

Layer 1: 02
         22

Layer 2: 11
         22

Layer 3: 22
         12

Layer 4: 00
         00
Then, the full image can be found by determining the top visible pixel in each position:

The top-left pixel is black because the top layer is 0.
The top-right pixel is white because the top layer is 2 (transparent), but the second layer is 1.
The bottom-left pixel is white because the top two layers are 2, but the third layer is 1.
The bottom-right pixel is black because the only visible pixel in that position is 0 (from layer 4).
So, the final image looks like this:

01
10
What message is produced after decoding your image?
'''

import sys

def squash(layers):
    image_out = []
    for x in range(len(layers[0][0])):
        image_out.append([2] * len(layers[0][0][0]))
    
    to_continue = True
    for layer in layers:
        for image in layer:
            for image_row, y in zip(image, range(len(image))):
                for pixel, x in zip(image_row, range(len(image_row))):
                    if image_out[y][x] == 2:
                        image_out[y][x] = int(pixel)

    return image_out

def generate_layers(data, wide=25, tall=6):
    layers = []
    idx = 0 
    img_idx = 0
    while idx < len(data):
        begin_pos = wide * tall * img_idx
        end_pos =  wide * tall * (img_idx + 1)
        layers.append([[data[begin_pos : end_pos][row * wide : (row + 1) * wide] for row in range(tall)]])
        img_idx += 1
        idx = end_pos
        
     
    return layers

def parse_file(file_path : str):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.extend(list(line))
    return data

def main(argv):
    layers = generate_layers(parse_file(argv[1]), int(argv[2]), int(argv[3]))
    image = squash(layers)
    print('Image print is \n{}'.format('\n'.join([''.join([str(n) for n in row]).replace('0', ' ') for row in image])))

    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
