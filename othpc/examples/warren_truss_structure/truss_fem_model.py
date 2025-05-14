#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from truss_plot import plot_truss_structure

# Material and section properties
E = 210e9      # Young's modulus (Pa)
A = 0.01       # Cross-sectional area (m^2)

# Geometry
n_panels = 6  # One more panel than before
panel_length = 1.0
height = 1.0

# Generate nodes
nodes = []
for i in range(n_panels + 1):
    nodes.append([i * panel_length, 0.0])                    # bottom nodes (0 to 6)
for i in range(n_panels):
    nodes.append([(i + 0.5) * panel_length, height])         # top nodes (7 to 12)

nodes = np.array(nodes)
n_nodes = len(nodes)
DOF = 2
n_dofs = n_nodes * DOF

# Define elements
elements = []

# Bottom chord
for i in range(n_panels):
    elements.append((i, i + 1))

# Top chord
top_offset = n_panels + 1
for i in range(n_panels - 1):
    elements.append((top_offset + i, top_offset + i + 1))

# Diagonals
for i in range(n_panels):
    if i % 2 == 0:
        elements.append((i, top_offset + i))         # up-right
        elements.append((top_offset + i, i + 1))     # down-right
    else:
        elements.append((i + 1, top_offset + i))     # up-left
        elements.append((top_offset + i, i))         # down-left

# Assemble global stiffness matrix
K_global = np.zeros((n_dofs, n_dofs))

def element_stiffness(E, A, xi, xj):
    L = np.linalg.norm(xj - xi)
    c = (xj[0] - xi[0]) / L
    s = (xj[1] - xi[1]) / L
    k = E * A / L
    ke = k * np.array([
        [ c*c,  c*s, -c*c, -c*s],
        [ c*s,  s*s, -c*s, -s*s],
        [-c*c, -c*s,  c*c,  c*s],
        [-c*s, -s*s,  c*s,  s*s]
    ])
    return ke

# Build K_global
for (i, j) in elements:
    xi = nodes[i]
    xj = nodes[j]
    ke = element_stiffness(E, A, xi, xj)
    dof_map = [i*DOF, i*DOF+1, j*DOF, j*DOF+1]
    for a in range(4):
        for b in range(4):
            K_global[dof_map[a], dof_map[b]] += ke[a, b]

# Force vector: uniform vertical load on all upper nodes
F = np.zeros(n_dofs)
uniform_load = -2000  # N per node (downward)

bottom_nodes = range(n_panels + 1)  # nodes 0 to 6
for node in bottom_nodes:
    F[node * DOF + 1] = uniform_load # Apply vertical force (Y-direction)

# Boundary conditions: fix both ends (node 0 and node 6)
fixed_dofs = [0, 1, 6 * DOF, 6 * DOF + 1]

# Solve
all_dofs = np.arange(n_dofs)
free_dofs = np.setdiff1d(all_dofs, fixed_dofs)

K_ff = K_global[np.ix_(free_dofs, free_dofs)]
F_f = F[free_dofs]

u = np.zeros(n_dofs)
u[free_dofs] = np.linalg.solve(K_ff, F_f)

# Reaction forces
reactions = K_global @ u - F

# Max displacement
displacements = u.reshape(-1, 2)
magnitudes = np.linalg.norm(displacements, axis=1)
max_disp = np.max(magnitudes)
max_node = np.argmax(magnitudes)

# Output
print("Max displacement: {:.6e} m at node {}".format(max_disp, max_node))
print("Displacement at node {}: {}".format(max_node, displacements[max_node]))

plot_truss_structure(nodes, elements, displacements, reactions, uniform_load,
                     bottom_nodes=list(range(7)), support_nodes=[0, 6])
