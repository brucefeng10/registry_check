# coding: utf-8
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = ""
from crnn import keys
from crnn import util
from crnn import dataset
from crnn.models import crnn as crnn
import torch
import torch.utils.data
from collections import OrderedDict
from PIL import Image
from torch.autograd import Variable


alphabet = keys.alphabetChinese
LSTMFLAG = False


def predict_img(imgpath):
    converter = util.strLabelConverter(alphabet)
    model = crnn.CRNN(32, 1, len(alphabet) + 1, 256, 1, lstmFlag=LSTMFLAG).cpu()
    ocrModel = './ocr-dense.pth'
    # ocrModel = './models/ocr-dense.pth'
    state_dict = torch.load(ocrModel, map_location=lambda storage, loc: storage)
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k.replace('module.', '')  # remove `module.`
        new_state_dict[name] = v
    # load params

    model.load_state_dict(new_state_dict)
    model.eval()
    # imgpath = 'j8yc.png'
    image = Image.open(imgpath).convert('L')
    scale = image.size[1] * 1.0 / 32
    w = image.size[0] / scale
    w = int(w)
    # print "im size:{},{}".format(image.size,w)
    transformer = dataset.resizeNormalize((w, 32))
    image = transformer(image).cpu()
    image = image.view(1, *image.size())
    image = Variable(image)
    model.eval()
    preds = model(image)
    _, preds = preds.max(2)
    preds = preds.transpose(1, 0).contiguous().view(-1)
    preds_size = Variable(torch.IntTensor([preds.size(0)]))
    sim_pred = converter.decode(preds.data, preds_size.data, raw=False)

    # print(sim_pred)
    return sim_pred


if __name__ == '__main__':
    imgpath = './hanzi.png'
    result = predict_img(imgpath)
    print('Prediction: ', result)


