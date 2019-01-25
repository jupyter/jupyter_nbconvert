import os

import nbformat
from ..snapshot import SnapshotPreProcessor
from ..execute import ExecutePreprocessor
import PIL.Image
try:
    from io import BytesIO as StringIO
except:
    from cStringIO import StringIO
import base64

current_dir = os.path.dirname(__file__)

def test_red_pixel():
    execute_preprocessor = ExecutePreprocessor(enabled=True)

    input_file = os.path.join(current_dir, 'files', 'single-pixel.ipynb')
    spp = SnapshotPreProcessor(page_opener_class='headless')
    nb = nbformat.read(input_file, 4)
    resources = {}
    nb, resources = execute_preprocessor.preprocess(nb, resources)
    assert 'image/png' not in nb.cells[0].outputs[0].data
    nb, resources = spp.preprocess(nb, resources)
    assert 'image/png' in nb.cells[0].outputs[0].data
    # we cannot be sure the browser encodes it the same way
    # assert nb.cells[0].outputs[0].data['image/png'] == 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNIOfHrPwAG4AMmv//laQAAAABJRU5ErkJggg=='
    # instead, we read the magic pixel values
    f = StringIO(base64.b64decode(nb.cells[0].outputs[0].data['image/png']))
    image = PIL.Image.open(f)
    pixel = image.getpixel((0, 0))
    assert pixel == (100, 200, 250, 255)
