"""
This file reads a file of smiles strings and generates a 
hand-drawn chemical structure dataset of these molecules.

1. Collect smiles strings from txt file
2. Collect background images
3. For each smiles string:
    3a. Convert smiles string to ong of molecule
    3b. Augment molecule image using molecule 
        augmentation pipeline
    3c. Randomly select background image
    3d. Augment background image using background
        augmentation pipeline
    3e. Combine augmented molecule and augmented background
        using random weighted addition
    3f. Degrade total image
    3g. Save image to folder 
"""
import cv2
import os
import glob
import numpy as np
import random 

from multiprocessing import Pool

import rdkit 
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Draw

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from RDKit_modified.mol_drawing import MolDrawing
from RDKit_modified.local_canvas import Canvas

from degrade import degrade_img
from augment import augment_mol, augment_bkg


def get_smiles(filename):
    ''' Read smiles data from *.formulas.txt file'''
    with open(filename) as f:
        lines = f.readlines()
    smiles = [s.split()[0] for s in lines]
    return smiles


def get_background_imgs(path):
    '''Reads in background dataset'''
    bkg_files = glob.glob("{}/*.png".format(path))
    bkgs = [cv2.imread(b) for b in bkg_files]
    return bkgs


def smiles_to_rdkitmod(s, i, img_dir):
    '''Generate RDKit image from smiles string'''
    m = Chem.MolFromSmiles(s)
    AllChem.Compute2DCoords(m)

    Draw.MolToFile(m, "{}/{}.png".format(img_dir, i), size=(256, 256), wedgeBonds=False)



def smiles_to_synthetic(s, i, img_dir):

    # Convert smiles string to RDKit' image
    smiles_to_rdkitmod(s, i, img_dir)
    mol = cv2.imread("{}/{}.png".format(img_dir,i))

    # Augment molecule imag
    mol_aug = augment_mol(mol)

    # Randomly select background image
    bkg = random.choice(bkgs)

    # Augment background image
    bkg_aug = augment_bkg(bkg)
    # bkg_aug = bkg

    p=0.3
    # q = np.random.uniform(0.1,0.5)
    mol_bkg = cv2.addWeighted(bkg_aug, p, mol_aug, 1-p, gamma=0)
    
    cv2.imwrite("{}/{}.png".format(img_dir,i), mol_bkg) 


if __name__ == "__main__":
    
    # RDKit settings
    Draw.DrawingOptions.wedgeBonds = False
    Draw.DrawingOptions.wedgeDashedBonds = False
    Draw.DrawingOptions.bondLineWidth = np.random.uniform(1,7)
    
    # Collect background images
    path_bkg = "../backgrounds/"
    bkgs = get_background_imgs(path_bkg)


    size = "temp"
    d = "train"   #["train", "val", "test"]
    # Make image directory
    img_dir = "{}/{}_images".format(size, d)
    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)

            
    smiles = "CS(=O)(=O)SCCO"
    idx = 5880

    # Build dataset
    # for idx, s in enumerate(smiles):
    smiles_to_synthetic(smiles, idx, img_dir)
    
    print ("   - Done.\n")


