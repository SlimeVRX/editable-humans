import os, sys
import logging as log
import numpy as np
import torch
import pickle
import random
from lib.models.evaluator import Evaluator
from lib.models.trainer import Trainer

from lib.utils.config import *
from lib.utils.image import update_edited_images

def main(config):
    
    # Set random seed.
    random.seed(config.seed)
    np.random.seed(config.seed)
    torch.manual_seed(config.seed)

    log_dir = config.pretrained_root

    with open('data/smpl_mesh.pkl', 'rb') as f:
        smpl_mesh = pickle.load(f)

    trainer = Trainer(config, smpl_mesh['smpl_V'], smpl_mesh['smpl_F'], log_dir)

    trainer.load_checkpoint(os.path.join(config.pretrained_root, config.model_name))


    evaluator = Evaluator(config, log_dir, mode='test')

    evaluator.init_models(trainer)

    evaluator.fitting_3D(32, 'data/test/mesh//mesh-f00190', 'data/test/mesh/mesh-f00190_smpl.obj', fit_rgb=True)
    evaluator.reconstruction(32, epoch=999)
    #rendered = evaluator.render_2D(32, epoch=999)

    rendered = update_edited_images('data/test/images', 'data/test/render_dict.pkl')

    evaluator.fitting_2D(32, rendered, 'data/test/mesh/mesh-f00190_smpl.obj')

    evaluator.reconstruction(32, epoch=998)

if __name__ == "__main__":

    parser = parse_options()
    parser.add_argument('--pretrained-root', type=str, required=True, help='pretrained model path')
    parser.add_argument('--model-name', type=str, required=True, help='load model name')

    args, args_str = argparse_to_str(parser)
    handlers = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(level=args.log_level,
                        format='%(asctime)s|%(levelname)8s| %(message)s',
                        handlers=handlers)
    logging.info(f'Info: \n{args_str}')
    main(args)