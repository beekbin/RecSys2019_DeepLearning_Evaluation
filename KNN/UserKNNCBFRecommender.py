#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 13/03/19

@author: Anonymous authors
"""

from Base.Recommender_utils import check_matrix
from Base.BaseSimilarityMatrixRecommender import BaseSimilarityMatrixRecommender
from Base.IR_feature_weighting import okapi_BM_25, TF_IDF
import numpy as np

from Base.Similarity.Compute_Similarity import Compute_Similarity


class UserKNNCBFRecommender(BaseSimilarityMatrixRecommender):
    """ UserKNN recommender"""

    RECOMMENDER_NAME = "UserKNNCBFRecommender"

    FEATURE_WEIGHTING_VALUES = ["BM25", "TF-IDF", "none"]

    def __init__(self, UCM, URM_train):
        super(UserKNNCBFRecommender, self).__init__(URM_train)

        self.UCM = UCM.copy()

        self._compute_item_score = self._compute_score_user_based


    def fit(self, topK=50, shrink=100, similarity='cosine', normalize=True, feature_weighting = "none", **similarity_args):

        self.topK = topK
        self.shrink = shrink

        if feature_weighting not in self.FEATURE_WEIGHTING_VALUES:
            raise ValueError("Value for 'feature_weighting' not recognized. Acceptable values are {}, provided was '{}'".format(self.FEATURE_WEIGHTING_VALUES, feature_weighting))


        if feature_weighting == "BM25":
            self.UCM = self.UCM.astype(np.float32)
            self.UCM = okapi_BM_25(self.UCM)

        elif feature_weighting == "TF-IDF":
            self.UCM = self.UCM.astype(np.float32)
            self.UCM = TF_IDF(self.UCM)


        similarity = Compute_Similarity(self.UCM.T, shrink=shrink, topK=topK, normalize=normalize, similarity = similarity, **similarity_args)

        self.W_sparse = similarity.compute_similarity()
        self.W_sparse = check_matrix(self.W_sparse, format='csr')

