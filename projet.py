from ursina import *
import random
import trimesh
import numpy as np
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.dropdown_menu import DropdownMenu, DropdownMenuButton
from ursina.prefabs.radial_menu import RadialMenu, RadialMenuButton

app = Ursina()


icosahedron_mesh = trimesh.creation.box(extents=[2, 2, 2])

vertices = icosahedron_mesh.vertices.tolist()
faces = icosahedron_mesh.faces.tolist()
normals = icosahedron_mesh.vertex_normals.tolist() #les normals correspondent à l'orientation des faces

# Génération de coordonnées UV simples (pour pouvoir appliquer les textures)
uvs = [[(v[0] + 1) / 2, (v[1] + 1) / 2] for v in vertices]

custom_mesh = Mesh(
    vertices=vertices,
    triangles=faces,
    normals=normals,
    uvs=uvs,
    mode='triangle'
)

dice = Entity(
    model=custom_mesh, 
    texture='brick',
    color='#ff0000',
    scale=2, 
    y=1, 
    shader=lit_with_shadows_shader
)

light = DirectionalLight(shadows=True)
light.look_at(Vec3(0.5, -1, -1))

selected_sides = 6 

def set_sides(n):
    global selected_sides
    global dice
    selected_sides = n
    sides_button.text = str(n)

    dice_mesh = create_dice(n)
    vertices = dice_mesh.vertices.tolist()
    faces = dice_mesh.faces.tolist()
    normals = dice_mesh.vertex_normals.tolist()
    uvs = [[(v[0] + 1) / 2, (v[1] + 1) / 2] for v in vertices]
    
    custom_mesh = Mesh(
        vertices=vertices,
        triangles=faces,
        normals=normals,
        uvs=uvs,
        mode='triangle'
    )
    if 'dice' in globals() and dice:
            dice.disable()
            destroy(dice)
        
    dice = Entity(
        model=custom_mesh,
        texture='brick',
        color='#ff0000',
        scale=2,
        y=1,
        shader=lit_with_shadows_shader
    )

def create_dice(n):
    if n == 4:  # Tétraèdre
        vertices = [
            [0, 0, 1], 
            [0.943, 0, -0.333], 
            [-0.471, 0.816, -0.333], 
            [-0.471, -0.816, -0.333]
        ]
        faces = [[0, 1, 2], [0, 2, 3], [0, 3, 1], [1, 3, 2]]
        return trimesh.Trimesh(vertices=vertices, faces=faces)
        
    elif n == 6:  # Cube
        return trimesh.creation.box(extents=[2, 2, 2])
        
    elif n == 8:  # Octaèdre
        vertices = [
            [1, 0, 0], [-1, 0, 0], 
            [0, 1, 0], [0, -1, 0], 
            [0, 0, 1], [0, 0, -1]
        ]
        faces = [
            [0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2],
            [1, 4, 2], [1, 3, 4], [1, 5, 3], [1, 2, 5]
        ]
        return trimesh.Trimesh(vertices=vertices, faces=faces)
    
    elif n == 10:  # Pentagonal antiprisme
        vertices = []
        # Pentagone supérieur
        for i in range(5):
            angle = 2 * np.pi * i / 5
            vertices.append([np.cos(angle), np.sin(angle), 0.5])
        # Pentagone inférieur (tourné)
        for i in range(5):
            angle = 2 * np.pi * (i + 0.5) / 5
            vertices.append([np.cos(angle), np.sin(angle), -0.5])
        
        faces = []
        for i in range(5):
            faces.append([i, (i+1)%5, i+5])
        for i in range(5):
            faces.append([(i+1)%5, (i+1)%5+5, i+5])
        
        return trimesh.Trimesh(vertices=vertices, faces=faces)
        
    elif n == 12:  # Dodécaèdre
        phi = (1 + np.sqrt(5)) / 2
        vertices = [
            [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
            [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
            [0, phi, 1/phi], [0, phi, -1/phi], [0, -phi, 1/phi], [0, -phi, -1/phi],
            [1/phi, 0, phi], [1/phi, 0, -phi], [-1/phi, 0, phi], [-1/phi, 0, -phi],
            [phi, 1/phi, 0], [phi, -1/phi, 0], [-phi, 1/phi, 0], [-phi, -1/phi, 0]
        ]
        
        faces = [
            [0, 8, 4, 14, 12], [0, 16, 17, 2, 12], [0, 8, 9, 1, 16],
            [1, 9, 5, 15, 13], [1, 16, 17, 3, 13], [2, 10, 6, 14, 12],
            [2, 10, 11, 3, 17], [3, 11, 7, 15, 13], [4, 8, 9, 5, 18],
            [4, 18, 19, 6, 14], [5, 18, 19, 7, 15], [6, 10, 11, 7, 19]
        ]
        return trimesh.Trimesh(vertices=vertices, faces=faces)
        
    elif n == 20:  # Icosaèdre
        return trimesh.creation.icosahedron()
    

radialmenu = RadialMenu(
    text='6',
    buttons=(
        RadialMenuButton(text='4', on_click=Func(set_sides, 4)),
        RadialMenuButton(text='6', on_click=Func(set_sides, 6)),
        RadialMenuButton(text='8', on_click=Func(set_sides, 8)),
        RadialMenuButton(text='20', on_click=Func(set_sides, 20)),
    ),
    enabled = False
)

Text(text='Number of sides:', x=-.575, y=-.15, scale=0.7)
sides_button = Button(
    text='6',
    x=-.5,
    y=-.2,
    scale=(0.1, 0.05),
    on_click=Func(setattr, radialmenu, 'enabled', True)
)

roll_button = Button(text='Roll Dice', y=-.3, scale=(0.2, 0.05), color=color.azure)
result_text = Text(text='Result: ', position=(-0.7, 0.4), scale=1.5)

def roll_dice():
    
    dice.rotation = (0, 0, 0)
    dice.position = (0, 1, 0)
    
    target_rotation = (random.uniform(0,360), random.uniform(0,360), random.uniform(0,360))
    dice.animate_rotation(target_rotation, duration=2, curve=curve.in_out_expo)
    dice.animate_position((0, 1.5, 0), duration=0.5, curve=curve.out_quad)
    dice.animate_position((0, 1, 0), duration=0.5, delay=0.5, curve=curve.in_quad)
    
    result = random.randint(1, selected_sides)
    invoke(set_result, result, delay=2)

def set_result(result):
    result_text.text = f'Result: {result}'
    result_text.color = color.green
    invoke(lambda: setattr(result_text, 'color', color.white), delay=0.5)

roll_button.on_click = roll_dice

Text(
    text='(You can orbit camera with right mouse button)', 
    position=(-0.85, -0.45), 
    scale=0.7, 
    color=color.gray
)

EditorCamera()

app.run()
