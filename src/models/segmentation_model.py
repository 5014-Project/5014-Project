"""
Segmentation_Model.py

This file contains the implementation of the Segmentation Model for the Behavioral and Segmentation Agent.
The model segments and classifies appliance usage patterns to determine the priority of smart home appliance usage.

Usage:
- This model is used by the Behavioral and Segmentation Agent to analyze and classify appliance-level energy usage.
- It employs clustering techniques to segment different appliance usage behaviors.

Inputs:
- Appliance-level energy consumption data.

Outputs:
- Segmentation results indicating appliance usage categories and their respective priorities.

Dependencies:
- Scikit-learn for clustering implementation.

"""

from sklearn.cluster import KMeans
import numpy as np

class SegmentationModel:
    def __init__(self, n_clusters=3):
        """
        Initializes the Segmentation Model with a specified number of clusters.

        Args:
        n_clusters (int): Number of clusters for segmenting appliance usage patterns.
        """
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=self.n_clusters)

    def fit(self, data):
        """
        Fits the KMeans model on the provided appliance usage data.

        Args:
        data (np.array): Appliance-level energy consumption data for clustering.
        """
        self.model.fit(data)
        print("Segmentation model trained with the given data.")

    def predict(self, data):
        """
        Predicts the cluster for each data point (appliance usage pattern).

        Args:
        data (np.array): Appliance-level energy consumption data to be segmented.

        Returns:
        np.array: Array of cluster labels for each data point.
        """
        clusters = self.model.predict(data)
        print(f"Predicted clusters: {clusters}")
        return clusters

    def get_cluster_centers(self):
        """
        Retrieves the centers of the clusters.

        Returns:
        np.array: Array of cluster center points.
        """
        return self.model.cluster_centers_

# Example usage
if __name__ == "__main__":
    # Sample appliance usage data (random data for demonstration)
    sample_data = np.random.rand(10, 5)  # 10 samples with 5 features each

    segmentation_model = SegmentationModel(n_clusters=3)
    segmentation_model.fit(sample_data)
    clusters = segmentation_model.predict(sample_data)
    print("Cluster Centers:", segmentation_model.get_cluster_centers())
