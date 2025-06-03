#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

def plot_truss_structure(nodes, elements, displacements, reactions, uniform_load,
                         bottom_nodes, support_nodes,
                         scale=2000, arrow_scale=1e-5, load_scale=2e-4):
    """
    Plots the undeformed and deformed truss structure with support reactions and applied forces.

    Parameters:
        nodes (ndarray): N x 2 array of original node coordinates.
        
        elements (list of tuple): List of (i, j) element node index pairs.
        
        displacements (ndarray): N x 2 array of nodal displacements.
        
        reactions (ndarray): 2N array of reaction force components.
        
        uniform_load : float of the uniform load applied at each bottom node

        bottom_nodes (list or range): Indices of bottom nodes with applied loads.
        
        support_nodes (list): Indices of support nodes.
        
        scale (float): Deformation magnification factor.
        
        arrow_scale (float): Scaling factor for reaction arrow length.
        
        load_scale (float): Scaling factor for applied load arrow length.
    """
    fig, ax = plt.subplots(figsize=(12, 4))

    # Undeformed truss
    for (i, j) in elements:
        xi, xj = nodes[i], nodes[j]
        ax.plot([xi[0], xj[0]], [xi[1], xj[1]], 'lightgray', linewidth=1)

    # Deformed truss
    deformed_nodes = nodes + scale * displacements
    for (i, j) in elements:
        xi, xj = deformed_nodes[i], deformed_nodes[j]
        ax.plot([xi[0], xj[0]], [xi[1], xj[1]], 'C0', linewidth=2)

    # Plot nodes
    ax.plot(nodes[:, 0], nodes[:, 1], 'ko', markersize=3, label="Original nodes")
    ax.plot(deformed_nodes[:, 0], deformed_nodes[:, 1], 'C1o', markersize=3, label="Deformed nodes")

    # Support reaction arrows
    DOF = 2
    for idx, node in enumerate(support_nodes):
        x, y = nodes[node]
        fx = reactions[node * DOF]
        fy = reactions[node * DOF + 1]
        ax.arrow(x, y, arrow_scale * fx, arrow_scale * fy,
                 head_width=0.1, head_length=0.2, fc='green', ec='green',
                 label='Reaction' if idx == 0 else "")

    # Applied load arrows (assumes vertical force only)
    for node in bottom_nodes:
        x, y = nodes[node]
        ax.arrow(x, y, 0, load_scale * uniform_load,
                head_width=0.1, head_length=0.2, fc='C3', ec='C3', label='Applied force' if node == bottom_nodes[0] else "")

    # Formatting
    ax.set_aspect('equal')
    ax.set_title(f"Truss: Undeformed (gray), Deformed (blue, x{scale})\nGreen: Reactions, Red: Applied Forces")
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.grid(True)
    ax.legend()
    plt.savefig("displacement.png", dpi=300)
