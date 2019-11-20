import randomizePointCloud
import pcSamplingRayShapenet
from easydict import EasyDict

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--shapenet_path", help="Input Folder", required=True)
    parser.add_argument('--virtualscan', type=str, help='Path to the virtual scanner executable', default='virtual_scanner/build/virtualscanner')
	parser.add_argument("--limit", help="Max number of points in the output cloud", default=0, type=int)

	args = parser.parse_args()
	pcSamplingRayShapenet.shoot_rays(EasyDict(args.__dict__))
	randomizePointCloud.shuffle_folder(EasyDict(args.__dict__))


if __name__ == "__main__":
	main()
