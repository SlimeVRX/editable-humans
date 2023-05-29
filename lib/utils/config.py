import argparse
import pprint
import yaml
import logging

def parse_options():

    parser = argparse.ArgumentParser(description='Custom Humans Code')


    ###################
    # Global arguments
    ###################
    global_group = parser.add_argument_group('global')
    global_group.add_argument('--config', type=str, default='config.yaml', 
                               help='Path to config file to replace defaults')
    global_group.add_argument('--save-root', type=str, default='./checkpoints/', 
                               help="outputs path")
    global_group.add_argument('--exp-name', type=str, default='test',
                               help="Experiment name.")
    global_group.add_argument('--seed', type=int, default=123)
    global_group.add_argument('--resume', type=str, default=None,
                                help='Resume from the checkpoint.')
    global_group.add_argument(
        '--log_level', action='store', type=int, default=logging.INFO,
        help='Logging level to use globally, DEBUG: 10, INFO: 20, WARN: 30, ERROR: 40.')
        
    ###################
    # Arguments for dataset
    ###################
    data_group = parser.add_argument_group('dataset')
    data_group.add_argument('--data-root', type=str, default='CustomHumans.h5',
                            help='Path to dataset')
    data_group.add_argument('--num-samples', type=int, default=20480,
                            help='Number of samples to use for each subject during training')
    data_group.add_argument('--repeat-times', type=int, default=8,
                            help='Number of times to repeat each subject during training')


    ###################
    # Arguments for optimizer
    ###################
    optim_group = parser.add_argument_group('optimizer')
    optim_group.add_argument('--lr-codebook', type=float, default=0.001, 
                             help='Learning rate for the codebook.')
    optim_group.add_argument('--lr-decoder', type=float, default=0.001, 
                             help='Learning rate for the decoder.')
    optim_group.add_argument('--lr-dis', type=float, default=0.004,
                                help='Learning rate for the discriminator.')
    optim_group.add_argument('--beta1', type=float, default=0.5,
                                help='Beta1.')
    optim_group.add_argument('--beta2', type=float, default=0.999,
                                help='Beta2.')
    optim_group.add_argument('--weight-decay', type=float, default=0, 
                             help='Weight decay.')


    ###################
    # Arguments for training
    ###################
    train_group = parser.add_argument_group('train')
    train_group.add_argument('--epochs', type=int, default=800, 
                             help='Number of epochs to run the training.')
    train_group.add_argument('--batch-size', type=int, default=2, 
                             help='Batch size for the training.')
    train_group.add_argument('--workers', type=int, default=0,
                             help='Number of workers for the data loader. 0 means single process.')
    train_group.add_argument('--save-every', type=int, default=50, 
                             help='Save the model at every N epoch.')
    train_group.add_argument('--log-every', type=int, default=100,
                             help='write logs to wandb at every N iters')
    train_group.add_argument('--use-2d-from-epoch', type=int, default=-1,
                             help='Adding 2D loss from this epoch. -1 indicates not using 2D loss.')
    train_group.add_argument('--train-2d-every-iter', type=int, default=1,
                             help='Train 2D loss every N iterations.')
    train_group.add_argument('--use-nrm-dis', action='store_true',
                             help='train with normal loss discriminator.')
    train_group.add_argument('--use-cached-pts', action='store_true',
                             help='Use cached point coordinates instead of online raytracing during training.')

    ###################
    # Arguments for Feature Dictionary
    ###################
    sample_group = parser.add_argument_group('dictionary')
    sample_group.add_argument('--shape-dim', type=int, default=32,
                                help='Dimension of the shape feature code.')
    sample_group.add_argument('--color-dim', type=int, default=32,
                                help='Dimension of the color feature code.')
    sample_group.add_argument('--feature-std', type=float, default=0.1,
                                help='Standard deviation for initializing the feature code.')
    sample_group.add_argument('--feature-bias', type=float, default=0.1,
                                help='Bias for initializing the feature code.')
    sample_group.add_argument('--shape-pca-dim', type=int, default=8,
                                help='Dimension of the shape pca code.')
    sample_group.add_argument('--color-pca-dim', type=int, default=16,
                                help='Dimension of the color pca code.')
    
    ###################
    # Arguments for Network
    ###################
    net_group = parser.add_argument_group('network')
    net_group.add_argument('--pos-dim', type=int, default=3,
                          help='input position dimension')
    net_group.add_argument('--c-dim', type=int, default=0,
                          help='conditional input dimension, if 0, no conditional input')
    net_group.add_argument('--num-layers', type=int, default=4, 
                             help='Number of layers for the MLPs.')
    net_group.add_argument('--hidden-dim', type=int, default=128,
                          help='Network width')
    net_group.add_argument('--activation', type=str, default='relu',
                            choices=['relu', 'sin', 'softplus', 'lrelu'])
    net_group.add_argument('--layer-type', type=str, default='none',
                            choices=['none', 'spectral_norm', 'frobenius_norm', 'l_1_norm', 'l_inf_norm'])
    net_group.add_argument('--skip', type=int, nargs='*', default=[2],
                          help='Layer to have skip connection.')

    ###################
    # Embedder arguments
    ###################
    embedder_group = parser.add_argument_group('embedder')
    embedder_group.add_argument('--shape-freq', type=int, default=5,
                                help='log2 of max freq')
    embedder_group.add_argument('--color-freq', type=int, default=10,
                                help='log2 of max freq')


    ###################
    # Losses arguments
    ###################
    embedder_group = parser.add_argument_group('losses')
    embedder_group.add_argument('--lambda-sdf', type=float, default=1000,
                                help='lambda for sdf loss')
    embedder_group.add_argument('--lambda-rgb', type=float, default=150,
                                help='lambda for rgb loss')
    embedder_group.add_argument('--lambda-nrm', type=float, default=10,
                                help='lambda for normal loss')
    embedder_group.add_argument('--lambda-reg', type=float, default=1,
                                help='lambda for regularization loss')
    embedder_group.add_argument('--gan-loss-type', type=str, default='logistic',
                                choices=['logistic', 'hinge'],
                                help='loss type for gan loss')
    embedder_group.add_argument('--lambda-gan', type=float, default=1,  
                                help='lambda for gan loss')
    embedder_group.add_argument('--lambda-grad', type=float, default=10,
                                help='lambda for gradient penalty')

   ###################
    # Arguments for validation
    ###################
    valid_group = parser.add_argument_group('validation')
    valid_group.add_argument('--valid-every', type=int, default=10,
                             help='Frequency of running validation.')
    valid_group.add_argument('--subdivide', type=bool, default=True, 
                            help='Subdivide the mesh before marching cubes')
    valid_group.add_argument('--grid-size', type=int, default=300, 
                            help='Grid size for marching cubes')
    valid_group.add_argument('--width', type=int, default=1024, 
                            help='Image width (height) for rendering')
    valid_group.add_argument('--fov', type=float, default=20.0, 
                            help='Field of view for rendering')
    valid_group.add_argument('--n_views', type=int, default=4, 
                            help='Number of views for rendering')

    ###################
    # Arguments for wandb
    ###################
    wandb_group = parser.add_argument_group('wandb')
    
    wandb_group.add_argument('--wandb-id', type=str, default=None,
                             help='wandb id')
    wandb_group.add_argument('--wandb', action='store_true',
                             help='Use wandb')
    wandb_group.add_argument('--wandb-name', default='default', type=str,
                             help='wandb_name')

    return parser


def parse_yaml_config(config_path, parser):
    """Parses and sets the parser defaults with a yaml config file.

    Args:
        config_path : path to the yaml config file.
        parser : The parser for which the defaults will be set.
        parent : True if parsing the parent yaml. Should never be set to True by the user.
    """
    with open(config_path) as f:
        config_dict = yaml.safe_load(f)

    list_of_valid_fields = []
    for group in parser._action_groups:
        group_dict = {list_of_valid_fields.append(a.dest) for a in group._group_actions}
    list_of_valid_fields = set(list_of_valid_fields)
    
    defaults_dict = {}

    # Loads child parent and overwrite the parent configs
    # The yaml files assumes the argument groups, which aren't actually nested.
    for key in config_dict:
        for field in config_dict[key]:
            if field not in list_of_valid_fields:
                raise ValueError(
                    f"ERROR: {field} is not a valid option. Check for typos in the config."
                )
            defaults_dict[field] = config_dict[key][field]


    parser.set_defaults(**defaults_dict)

def argparse_to_str(parser, args=None):
    """Convert parser to string representation for Tensorboard logging.

    Args:
        parser (argparse.parser): Parser object. Needed for the argument groups.
        args : The parsed arguments. Will compute from the parser if None.
    
    Returns:
        args    : The parsed arguments.
        arg_str : The string to be printed.
    """
    
    if args is None:
        args = parser.parse_args()

    if args.config is not None:
        parse_yaml_config(args.config, parser)

    args = parser.parse_args()

    args_dict = {}
    for group in parser._action_groups:
        group_dict = {a.dest: getattr(args, a.dest, None) for a in group._group_actions}
        args_dict[group.title] = vars(argparse.Namespace(**group_dict))

    pp = pprint.PrettyPrinter(indent=2)
    args_str = pp.pformat(args_dict)
    args_str = f'```{args_str}```'

    return args, args_str