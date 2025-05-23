from ursina import *
import random
import trimesh
import numpy as np
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.dropdown_menu import DropdownMenu, DropdownMenuButton
from ursina.prefabs.radial_menu import RadialMenu, RadialMenuButton

app = Ursina()

sky = Sky()

selected_sides = 6 
dice = None

def set_sides(n):
    """Permet la création d'un dé à n faces"""
    global selected_sides
    global dice
    selected_sides = n
    sides_button.text = str(n)

    dice_mesh = create_dice(n)
    vertices = dice_mesh.vertices.tolist()
    normals = dice_mesh.face_normals.tolist()
    #trimesh met les faces dans le sens inverse de celui voulu par ursina, on les inverses donc
    faces = [face[::-1] for face in dice_mesh.faces.tolist()]

    new_vertices = []
    new_faces = []
    new_normals = []

    # duplication des sommets (vertices) pour éviter le lissage des arretes
    for i, face in enumerate(faces):
        v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
        new_vertices.extend([v0, v1, v2])
        new_faces.append([3*i, 3*i+1, 3*i+2])
        new_normals.extend([normals[i]] * 3)
    
    custom_mesh = Mesh(
        vertices=new_vertices,
        triangles=new_faces,
        normals=new_normals,
        mode='triangle'
    )
    if 'dice' in globals() and dice:
            dice.disable()
            destroy(dice)
    
    dice = Entity(
        model=custom_mesh,
        color='6800ff',
        scale=2,
        y=1,
        shader=lit_with_shadows_shader
    )


def create_dice(n):
    """Permet la création Mesh en fonction du nombre de face donné"""
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
        
    elif n == 20:  # Icosaèdre
        return trimesh.creation.icosahedron()
    
radialmenu = RadialMenu(
    text='20',
    buttons=(
        RadialMenuButton(text='4', on_click=Func(set_sides, 4)),
        RadialMenuButton(text='6', on_click=Func(set_sides, 6)),
        RadialMenuButton(text='8', on_click=Func(set_sides, 8)),
        RadialMenuButton(text='20', on_click=Func(set_sides, 20)),
    ),
    enabled = False
)

Text(text='Number of sides:', x=-.575, y=-.15, scale=0.7, color=color.black)
sides_button = Button(
    text='6',
    x=-.5,
    y=-.2,
    scale=(0.1, 0.05),
    on_click=Func(setattr, radialmenu, 'enabled', True)
)

roll_button = Button(text='Roll Dice', y=-.3, scale=(0.2, 0.05), color=color.azure)
result_text = Text(text='Result: ', position=(-0.7, 0.4), scale=1.5, color=color.black)

def roll_dice():
    """Permet de faire tourner le dé dans une direction aléatoire"""
    dice.rotation = (0, 0, 0)
    dice.position = (0, 1, 0)
    
    target_rotation = (random.uniform(0,360), random.uniform(0,360), random.uniform(0,360))
    dice.animate_rotation(target_rotation, duration=2, curve=curve.in_out_expo)
    dice.animate_position((0, 1.5, 0), duration=0.5, curve=curve.out_quad)
    dice.animate_position((0, 1, 0), duration=0.5, delay=0.5, curve=curve.in_quad)
    
    result = random.randint(1, selected_sides)
    invoke(set_result, result, delay=2)

def set_result(result):
    """Permet d'actualiser le résultat dans le Text: result_text"""
    result_text.text = f'Result: {result}'
    result_text.color = color.green
    invoke(lambda: setattr(result_text, 'color', color.black), delay=0.5)

roll_button.on_click = roll_dice

Text(
    text='(You can orbit camera with right mouse button)', 
    position=(-0.85, -0.45), 
    scale=0.7, 
    color=color.gray
)

#initialisation du premier dé à 20 faces
set_sides(20)

camera = EditorCamera()

light = DirectionalLight(shadows=True)
light.parent = camera
light.look_at(Vec3(0, 0, 1))

app.run()