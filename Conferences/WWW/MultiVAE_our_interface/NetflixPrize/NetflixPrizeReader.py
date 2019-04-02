#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 06/01/18

@author: Anonymous authors
"""


import pickle, os
import scipy.sparse as sps
import pandas as pd
from Base.Recommender_utils import reshapeSparse

from Conferences.WWW.MultiVAE_our_interface.VAE_CF_data_splitter import split_train_validation_test_VAE_CF
from Data_manager.NetflixPrize.NetflixPrizeReader import NetflixPrizeReader as NetflixPrizeReader_DataManager
from Data_manager.load_and_save_data import save_data_dict, load_data_dict

class NetflixPrizeReader(object):

    def __init__(self):

        super(NetflixPrizeReader, self).__init__()

        pre_splitted_path = "Data_manager_split_datasets/NetflixPrize/WWW/MultiVAE_our_interface/"

        pre_splitted_filename = "splitted_data"

        # If directory does not exist, create
        if not os.path.exists(pre_splitted_path):
            os.makedirs(pre_splitted_path)

        try:

            print("NetflixPrizeReader: Attempting to load pre-splitted data")

            for attrib_name, attrib_object in load_data_dict(pre_splitted_path, pre_splitted_filename).items():
                 self.__setattr__(attrib_name, attrib_object)


        except FileNotFoundError:

            print("NetflixPrizeReader: Pre-splitted data not found, building new one")

            data_reader = NetflixPrizeReader_DataManager()
            data_reader.load_data()

            URM_all = data_reader.get_URM_all()

            # binarize the data (only keep ratings >= 4)
            URM_all.data = URM_all.data >= 4.0
            URM_all.eliminate_zeros()


            URM_all = sps.coo_matrix(URM_all)

            dict_for_dataframe = {"userId": URM_all.row,
                                  "movieId": URM_all.col,
                                  "rating": URM_all.data
                                }

            URM_all_dataframe = pd.DataFrame(data = dict_for_dataframe)


            self.URM_train, self.URM_train_all, self.URM_validation, self.URM_test = split_train_validation_test_VAE_CF(URM_all_dataframe,
                                                                                                                         n_heldout_users = 40000)


            n_rows = max(self.URM_train.shape[0], self.URM_train_all.shape[0], self.URM_validation.shape[0], self.URM_test.shape[0])
            n_cols = max(self.URM_train.shape[1], self.URM_train_all.shape[1], self.URM_validation.shape[1], self.URM_test.shape[1])

            newShape = (n_rows, n_cols)

            self.URM_test = reshapeSparse(self.URM_test, newShape)
            self.URM_train = reshapeSparse(self.URM_train, newShape)
            self.URM_train_all = reshapeSparse(self.URM_train_all, newShape)
            self.URM_test = reshapeSparse(self.URM_test, newShape)



            data_dict = {
                "URM_train": self.URM_train,
                "URM_train_all": self.URM_train_all,
                "URM_test": self.URM_test,
                "URM_validation": self.URM_validation,

            }

            save_data_dict(data_dict, pre_splitted_path, pre_splitted_filename)




            print("NetflixPrizeReader: Dataset loaded")



    #
    #
    # def _loadUserInteractions(self, data_folder_path):
    #
    #
    #     from data.IncrementalSparseMatrix import IncrementalSparseMatrix_LowRAM
    #
    #     numCells = 0
    #     URM_all_builder = IncrementalSparseMatrix_LowRAM(auto_create_col_mapper=True, auto_create_row_mapper=True)
    #
    #
    #     for current_split in [1, 2, 3, 4]:
    #
    #         current_split_path = data_folder_path + "combined_data_{}.txt".format(current_split)
    #
    #         fileHandle = open(current_split_path, "r")
    #
    #         print("NetflixPrizeReader: loading split {}".format(current_split))
    #
    #         currentMovie_id = None
    #
    #         for line in fileHandle:
    #
    #
    #             if numCells % 1000000 == 0 and numCells!=0:
    #                 print("Processed {} cells".format(numCells))
    #
    #             if (len(line)) > 1:
    #
    #                 line_split = line.split(",")
    #                 line_split[-1] = line_split[-1].replace("\n", "")
    #
    #                 # If line has 3 components, it is a 'user_id,rating,date' row
    #                 if len(line_split) == 3 and currentMovie_id!= None:
    #
    #                     numCells += 1
    #
    #                     user_id = line_split[0]
    #                     rating = float(line_split[1])
    #
    #                     if rating >= 4.0:
    #                         URM_all_builder.add_data_lists([user_id], [currentMovie_id], [1.0])
    #
    #
    #
    #                 # If line has 1 component, it MIGHT be a 'item_id:' row
    #                 elif len(line_split) == 1:
    #                     line_split = line.split(":")
    #
    #                     # Confirm it is a 'item_id:' row
    #                     if len(line_split) == 2:
    #                         currentMovie_id = line_split[0]
    #
    #                     else:
    #                         print("Unexpected row: '{}'".format(line))
    #
    #                 else:
    #                     print("Unexpected row: '{}'".format(line))
    #
    #
    #         fileHandle.close()
    #
    #
    #     return  URM_all_builder
    #
