from ursina import *
import random
import trimesh

app = Ursina()

icosahedron_mesh = trimesh.creation.icosahedron()

vertices = icosahedron_mesh.vertices.tolist()
faces = icosahedron_mesh.faces.tolist()
custom_mesh = Mesh(vertices=vertices, triangles=faces)

dice = Entity(model=custom_mesh, texture='grid.png', scale=2, y=1)

Text(text='Number of sides:', y=-.15, x=-0.2, scale=0.7)
n_input = InputField(
    text='6', 
    y=-.2, 
    scale=(0.2, 0.05),
    max_width=7
)
roll_button = Button(text='Roll Dice', y=-.3, scale=(0.2, 0.05), color=color.azure)
result_text = Text(text='Result: ', position=(-0.7, 0.4), scale=1.5)

def roll_dice():
    try:
        n = int(n_input.text)
        if n < 1:
            raise ValueError
    except:
        result_text.text = 'Invalid input'
        return
    
    dice.rotation = (0, 0, 0)
    dice.position = (0, 1, 0)
    
    target_rotation = (random.uniform(0,360), random.uniform(0,360), random.uniform(0,360))
    dice.animate_rotation(target_rotation, duration=2, curve=curve.in_out_expo)
    dice.animate_position((0, 1.5, 0), duration=0.5, curve=curve.out_quad)
    dice.animate_position((0, 1, 0), duration=0.5, delay=0.5, curve=curve.in_quad)
    
    result = random.randint(1, n)
    invoke(set_result, result, delay=2)

def set_result(result):
    result_text.text = f'Result: {result}'
    result_text.color = color.green
    invoke(lambda: setattr(result_text, 'color', color.white), delay=0.5)

roll_button.on_click = roll_dice

Text(text='(You can orbit camera with right mouse button)', 
     position=(-0.85, -0.45), 
     scale=0.7, 
     color=color.gray)


EditorCamera()

app.run()