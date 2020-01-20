import tkinter as tk
import time
import json
import timeit

ROWS = 30
COLUMNS = 30
WIDTH = 20
HEIGHT = 20
SLEEP = 0.01

#TODO let drag drop start and end points
#TODO add more algorithms


class App(tk.Tk):
    def __init__(self, *args, **kwargs):

        # initialize app
        tk.Tk.__init__(self, *args, **kwargs)
        self.canvas = tk.Canvas(self, width=(COLUMNS * WIDTH) + 15, height=(ROWS * HEIGHT),
                                borderwidth=2, highlightthickness=0)
        self.canvas.pack(anchor=tk.NW, fill="y", expand="false")
        self.rows = ROWS
        self.columns = COLUMNS
        self.tiles = {}
        self.walls = []
        self.method = 'Starting Point'
        self.algorithm = 'Euclidean'
        self.points = {'starting': [],
                       'ending': []}
        self.status = tk.Label(self, anchor="w")
        self.status.pack(side="bottom", fill="x")

        # create grid
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column * WIDTH
                y1 = row * HEIGHT
                x2 = x1 + WIDTH
                y2 = y1 + HEIGHT
                tile = self.canvas.create_rectangle(x1, y1, x2, y2, fill="grey", tags="rect")
                self.tiles[row, column] = tile
                self.canvas.tag_bind(tile, "<1>", lambda event, row=row, column=column: self.clicked(row, column))

        # create buttons
        for method in ["Starting Point", "Ending Point", "Build Walls", 'Remove Walls',
                       'Erase All', 'Save Layout', 'GO!']:
            button = tk.Button(self, text=method, command=lambda m=method: self.populate_method(m))
            button.pack(side=tk.LEFT)

        # create drop down menu
        self.dropVar = tk.StringVar()
        self.dropVar.set('Layout: 0')
        options = self.drop_down()
        w = tk.OptionMenu(self, self.dropVar, *options, command=self.layout)
        w.pack(side=tk.BOTTOM)

        self.dropVar2 = tk.StringVar()
        self.dropVar2.set('Euclidean')
        options2 = ['Euclidean', 'Pythagorean']
        w = tk.OptionMenu(self, self.dropVar2, *options2, command=self.drop_down2)
        w.pack(side=tk.BOTTOM)

        # create bindings
        self.bind("<B1-Motion>", self.click_drag)
        self.bind('<d>', self.debug)
        self.bind('<Return>', self.go)

    def drop_down(self):
        """Function: drop_down -- open up json file with saved layouts.
           Params:   n/a
           Returns:  list of the layout names

        """
        with open('walls.json') as json_file:
            data = json.load(json_file)
            return list(data.keys())

    def drop_down2(self, event):
        """Function: drop_down2 -- return what algo to run
           Params:   n/a
           Returns:  event

        """
        self.algorithm = event

    def layout(self, event):
        """Function: layout -- open up json file with saved layouts and updates layout and walls
           list with the selected layout
           Params:   event -- the option from the drop down menu that has been selected
           Returns:  n/a

        """
        with open('walls.json') as json_file:
            data = json.load(json_file)

        # updates the wall list based on layout selected
        for option in data.keys():
            if option == event:
                self.walls = data[option]

        # updates the walls on the grid
        for tile in self.tiles.values():
            self.canvas.itemconfigure(tile, fill='grey')

        for wall in self.walls:
            tile = self.tiles[wall[0], wall[1]]
            self.canvas.itemconfigure(tile, fill='black')

    def debug(self, event):
        """Function: debug -- prints start / end point and walls when 'd' is pressed
           Params:   n/a
           Returns:  n/a

        """
        print(f'start/end point: {self.points}')
        print(f'walls: {self.walls}')

    def populate_method(self, method):
        """Function: populate_method -- handles different buttons being pressed.
           Params:   method -- the name of the button that has been pressed
           Returns:  n/a

        """
        # update status message
        self.status.configure(text=f'Now selecting: {method}')
        self.method = method

        # Erase all method: delete everything
        if method == 'Erase All':
            for tile in self.tiles.values():
                self.canvas.itemconfigure(tile, fill='grey')
            self.walls = []
            self.points = {'starting': [],
                           'ending': []}

        # Go method: run go function
        elif method == 'GO!':
            self.go(None)

        # save layout method: save layout to json file
        elif self.method == 'Save Layout':
            with open('walls.json') as json_file:
                data = json.load(json_file)
                data[f'Layout: {len(data)}'] = self.walls

            with open('walls.json', 'w') as outfile:
                json.dump(data, outfile)
            self.status.configure(text=f'Layout successfully saved.')

    def clicked(self, row, column):
        """Function: clicked -- handles mouse clicks
           Params:   row -- integer of the row where mouse is clicked
                     column -- integer of the column where mouse is clicked
           Returns:  n/a

        """

        # get tile number based on row and column
        tile = self.tiles[row, column]
        new_color = 'grey'
        point = ''

        # if build wall method and wall doesn't exist on tile; add
        if self.method == 'Build Walls':
            new_color = 'black'
            if [row, column] not in self.walls:
                self.walls.append([row, column])

        # if remove wall method and wall exists on tile; remove
        elif self.method == 'Remove Walls':
            if [row, column] in self.walls:
                self.walls.remove([row, column])
                new_color = 'grey'

        # neither method is selected; get tile color
            else:
                new_color = self.canvas.itemcget(tile, 'fill')

        # update new_color and which point
        elif self.method == 'Ending Point':
            if [row, column] not in self.walls:
                new_color = 'red'
                point = 'ending'
            else:
                new_color = 'black'
        elif self.method == 'Starting Point':
            if [row, column] not in self.walls:
                new_color = 'green'
                point = 'starting'
                self.method = 'Ending Point'
            else:
                new_color = 'black'

        # if a point already exists, update old tile color to grey
        if point != '' and [row, column] not in self.walls:
            if len(self.points[point]) != 0:
                old_tile = self.tiles[self.points[point][0], self.points[point][1]]
                self.canvas.itemconfigure(old_tile, fill='grey')
                self.points[point] = [row, column]
            else:
                self.points[point] = [row, column]

        # update tile color to new color
        self.canvas.itemconfigure(tile, fill=new_color)

        # update status
        if self.method is None:
            self.status.configure(text=f'Please select a method!')
        else:
            self.status.configure(text=f'{self.method} at location: ({row},{column})')

    def click_drag(self, event):
        """Function: click_drag -- handles mouse click and drags
           Params:   event -- the coordinates of mouse when clicked and dragged
           Returns:  n/a

        """

        # converts coordinates to row / column
        row = event.y // HEIGHT
        column = event.x // WIDTH

        # if mouse click is within range of grid
        if (0 <= row <= (ROWS - 1)) and (0 <= column <= (COLUMNS - 1)):
            tile = self.tiles[row, column]

            # build walls
            if self.method == 'Build Walls':
                new_color = 'black'
                if [row, column] not in self.walls:
                    self.walls.append([row, column])
                    self.canvas.itemconfigure(tile, fill=new_color)
                    self.status.configure(text=f'Added wall at location: ({row},{column})')

            # remove walls
            elif self.method == 'Remove Walls':
                new_color = 'grey'
                if [row, column] in self.walls:
                    self.walls.remove([row, column])
                    self.canvas.itemconfigure(tile, fill=new_color)
                    self.status.configure(text=f'Removed wall at location: ({row},{column})')
            print(f'{row}/{column}. tile {tile}')

    def go(self, event):
        """Function: go -- runs algo
           Params:   n/a
           Returns:  n/a

        """

        # initiate node class
        node = Node()

        # test to see if start and end point have been selected
        if self.points['starting'] == [] or self.points['ending'] == []:
            self.status.configure(text='Missing start or ending point!')
        else:

            # reset grid
            for tile in self.tiles.values():
                self.canvas.itemconfigure(tile, fill='grey')

            for wall in self.walls:
                tile = self.tiles[wall[0], wall[1]]
                self.canvas.itemconfigure(tile, fill='black')
            tile = self.tiles[self.points['starting'][0], self.points['starting'][1]]
            self.canvas.itemconfigure(tile, fill='green')
            tile = self.tiles[self.points['ending'][0], self.points['ending'][1]]
            self.canvas.itemconfigure(tile, fill='red')
            # run algo
            try:
                start_time = time.process_time()
                path, closed_list = node.path_finding(self.points['starting'], self.points['ending'], self.walls)
                timed = time.process_time() - start_time
                # run paint function for checked tiles and correct path
                app.paint(closed_list, 'blue')
                app.paint(path, 'yellow')
                self.status.configure(text=f'{self.algorithm} algorithm took {timed:.5f} sec. to run.'
                                           f' Tested {len(closed_list)} tiles to find shortest path of'
                                           f' {len(path)} tiles.')
            # no path exists
            except TypeError as e:
                self.status.configure(text=f'No path exists!')

    def paint(self, nodes, color):
        """Function: paint -- handles animations of checked tiles and correct path
           Params:   nodes -- list of tiles that need to be colored
                     color -- what color to paint
           Returns:  n/a

        """
        # paint each node in the nodes list
        for node in nodes:
            tile = self.tiles[node.position[0], node.position[1]]
            self.canvas.itemconfigure(tile, fill=color)
            self.canvas.update()
            time.sleep(SLEEP)


class Node:
    """class:    Node
       Params:   parent -- node's parent
                 position --  list containing row / column of node's location
                 dist -- distance from starting node
                 e -- Euclidean distance from node to ending node
                 t -- dist + e

    """
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        # initialize node with dist, e, and t equaling 0
        self.dist = self.e = self.t = 0

    def __eq__(self, other):
        """Function: __eq__ -- handles comparison of two nodes
           Params:   other -- node on right side of expression
           Returns:  T/F if nodes have same position

        """
        return self.position == other.position

    def path_finding(self, start, end, walls):
        """Function: path_finding -- algorithm to find best path
           Params:   start -- list containing starting row / column
                     end -- list containing ending row / column
                     walls -- list containing row / column of each wall
           Returns:  path -- list of nodes that are best path
                     closed_list -- list of nodes that were tested while finding path

        """

        # create start and end nodes
        start_node = Node(None, start)
        end_node = Node(None, end)

        # calculate e and t of starting node
        if app.algorithm == 'Euclidean':
            start_node.e = abs(start_node.position[0] - end_node.position[0]) +\
                           abs(start_node.position[1] - end_node.position[1])
            start_node.t = start_node.dist + start_node.e
        else:
            start_node.e = ((start_node.position[0] - end_node.position[0]) ** 2) + \
                           ((start_node.position[1] - end_node.position[1]) ** 2)
            start_node.t = start_node.dist + start_node.e

        walls = walls

        # open_list will hold all nodes that need to be checked
        open_list = []

        # closed_list holds all nodes that have been checked
        closed_list = []

        # add starting node to open_list
        open_list.append(start_node)

        # run as long as there are still nodes in open list; default first node in list to current node
        while len(open_list) > 0:
            current_node = open_list[0]
            current_index = 0

            # check if any other nodes in current list have lower t value than current node;
            # if yes, that node is now current node
            for index, item in enumerate(open_list):
                if item.t < current_node.t:
                    current_node = item
                    current_index = index

            # remove current node from open list and put into closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # if current node equal end node; algo done return path and closed list
            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current)
                    current = current.parent
                return path[::-1], closed_list

            # find all children of current node
            children = []
            for new_position in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
                node_position = [current_node.position[0] + new_position[0],
                                              current_node.position[1] + new_position[1]]

                # if child not in grid; ignore
                if not 0 <= node_position[0] < ROWS or not 0 <= node_position[1] < COLUMNS:
                    continue

                # if child is a wall; ignore
                if node_position in walls:
                    continue

                # create new node at child position, with current node as parent; append to children list
                new_node = Node(current_node, node_position)
                children.append(new_node)

            # check children if not in open list or closed list, calculate dist, e, and t; append to open list
            for child in children:
                if child not in open_list and child not in closed_list:
                    child.dist = current_node.dist + 1
                    if app.algorithm == 'Euclidean':
                        child.e = abs(child.position[0] - end_node.position[0]) +\
                                  abs(child.position[1] - end_node.position[1])
                        child.t = child.dist + child.e
                    else:
                        child.e = ((child.position[0] - end_node.position[0]) ** 2) + \
                                       ((child.position[1] - end_node.position[1]) ** 2)
                        child.t = child.dist + child.e
                    open_list.append(child)


if __name__ == "__main__":
    app = App()
    app.title('Algo Visualizer')
    app.mainloop()
