'''
Intro to Artificial Intelligence Project 1
Dean Keinan, Ryan Lee
'''

import pygame, sys, math, random, heapq, os, time, resource
from random import randint
from ast import literal_eval as make_tuple

# Initialize Screen
pygame.init()
myfont = pygame.font.SysFont("courier new", 15)

TILESIZE = 6 
NUM_COL = 160
NUM_ROW = 120
DISPLAYSURF = pygame.display.set_mode((NUM_COL*TILESIZE+200,NUM_ROW*TILESIZE+50))

# Initialize graph
graph = [['1' for y in range(NUM_ROW)] for x in range(NUM_COL)]
start_x = 0
start_y = 0
goal_x = 1
goal_y = 1

pointer_x = 0
pointer_y = 0

hType = 1
heur = {1: "Manhattan", 2: "Euclidean", 3: "Octile", 4: "Chebyshev", 5: "Straight Diagonal Distance", 6: "Min Heurisitc Out of All", }
mem = None
# Make Random graph
def generate_graph():
	# Make 8 hard to traverse areas
	areasmade = 0
	areacoordinates = []
	while areasmade < 8:
		area_x = randint(0,NUM_COL-1)
		area_y = randint(0,NUM_ROW-1)

		if (area_x,area_y) not in areacoordinates:
			areacoordinates.append((area_x,area_y))
			for x in range(area_x-15,area_x+15):
				if x >= 0 and x < NUM_COL:
					for y in range(area_y-15,area_y+15):
						if y >= 0 and y < NUM_ROW:
							# 20% chance of this being hard to traverse
							if randint(0,9) < 5:
								graph[x][y] = '2'
			areasmade += 1

	# Make 4 highways
	highwaysmade = 0

	while highwaysmade < 4:
		makehighway = True
		highwaycells = []

		# Select a starting boundary
		x = randint(1,NUM_COL-2)
		y = randint(1,NUM_ROW-2)

		startside = randint(0,3)	# 0 = North, 1 = East, 2 = South, 3 = West
		if startside == 0:
			y = 0
			direction = 2
		elif startside == 1:
			x = NUM_COL-1
			direction = 3
		elif startside == 2:
			y = NUM_ROW-1
			direction = 0
		else:
			x = 0
			direction = 1

		travelled = 0
		totaltravelled = 0

		while True:
			# Quit if out of bounds
			if x<0 or x>=NUM_COL or y<0 or y>=NUM_ROW:
				break

			# Quit if crossed a river, do not make river
			if graph[x][y] == 'a' or graph[x][y] == 'b':
				makehighway = False
				break
			if (x,y) in highwaycells:
				makehighway = False
				break

			highwaycells.append((x,y))
			travelled += 1
			totaltravelled += 1

			# Move to next cell
			if direction == 0:
				y -= 1
			elif direction == 1:
				x += 1
			elif direction == 2:
				y += 1
			else:
				x -= 1

			# Change directions if travelled 20 cells
			if travelled >= 20:
				travelled = 0
				if randint(0,9) > 6:		# 40% chance change directions
					if direction == 0:
						direction = random.choice([1,3])
					elif direction == 1:
						direction = random.choice([0,2])
					elif direction == 2:
						direction = random.choice([1,3])
					else:
						direction = random.choice([0,2])

		if totaltravelled < 100:
			makehighway = False

		if makehighway == True:
			for cell in highwaycells:
				if graph[cell[0]][cell[1]] == '1':
					graph[cell[0]][cell[1]] = 'a'
				else:
					graph[cell[0]][cell[1]] = 'b'

			highwaysmade += 1

	# Blocked cells
	needtoblock = NUM_COL*NUM_ROW*0.2
	blocked = 0

	while blocked < needtoblock:
		x = randint(0,NUM_COL-1)
		y = randint(0,NUM_ROW-1)
		if graph[x][y]=='1' or graph[x][y]=='2':
			graph[x][y] = '0'
			blocked += 1

	# Return the coordinates of hard to traverse areas
	return areacoordinates

# Generate Start and Finish
def generate_endpoints():
	# Generate Start
	x = randint(0,39)
	y = randint(0,39)
	if x>20:
		x = NUM_COL-x+20
	if y>20:
		y = NUM_ROW-y+20

	while graph[x][y]=='a' or graph[x][y]=='b' or graph[x][y]=='0':
		x = randint(0,39)
		y = randint(0,39)
		if x>20:
			x = NUM_COL-x+20
		if y>20:
			y = NUM_ROW-y+20

	start_x = x
	start_y = y

	# Generate Finish
	while graph[x][y]=='a' or graph[x][y]=='b' or graph[x][y]=='0' or math.sqrt((x-start_x)**2+(y-start_y)**2)<100:
		x = randint(0,39)
		y = randint(0,39)
		if x>20:
			x = NUM_COL-x+20
		if y>20:
			y = NUM_ROW-y+20

	goal_x = x
	goal_y = y

	return start_x,start_y,goal_x,goal_y

# Draw graph
def draw(mygraphSurface):
	mygraphSurface.fill((255,255,255))
	for x in range(len(graph)):
		for y in range(len(graph[x])):
			if graph[x][y] == '0':
				pygame.draw.rect(mygraphSurface, (40,40,40), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE,TILESIZE), 0)
				pygame.draw.rect(mygraphSurface, (40,40,40), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE+1,TILESIZE+1), 1)
			elif graph[x][y] == '1':
				pygame.draw.rect(mygraphSurface, (255,255,255), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE,TILESIZE), 0)
				pygame.draw.rect(mygraphSurface, (100,100,100), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE+1,TILESIZE+1), 1)
			elif graph[x][y] == '2':
				pygame.draw.rect(mygraphSurface, (200,200,200), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE,TILESIZE), 0)
				pygame.draw.rect(mygraphSurface, (100,100,100), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE+1,TILESIZE+1), 1)
			elif graph[x][y] == 'a':
				pygame.draw.rect(mygraphSurface, (130,170,255), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE,TILESIZE), 0)
				pygame.draw.rect(mygraphSurface, (100,100,100), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE+1,TILESIZE+1), 1)
			elif graph[x][y] == 'b':
				pygame.draw.rect(mygraphSurface, (70,90,220), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE,TILESIZE), 0)
				pygame.draw.rect(mygraphSurface, (100,100,100), (x*TILESIZE+10,y*TILESIZE+10,TILESIZE+1,TILESIZE+1), 1)

	mygraphSurface = mygraphSurface.convert()
	return mygraphSurface

# Draw UI
def draw_ui(graphSurface,closed_list,path,pathcost,nodes_expanded,mode,elapsedtime,fn_g,fn_f,fn_h):

	DISPLAYSURF.blit(graphSurface,(0,0))

	pygame.draw.circle(DISPLAYSURF, (255,0,0), (start_x*TILESIZE+TILESIZE/2+10,start_y*TILESIZE+TILESIZE/2+10),TILESIZE/2, 0)
	pygame.draw.circle(DISPLAYSURF, (0,0,255), (goal_x*TILESIZE+TILESIZE/2+10,goal_y*TILESIZE+TILESIZE/2+10),TILESIZE/2, 0)

	pygame.draw.rect(DISPLAYSURF, (255,0,0), (pointer_x*TILESIZE+9,pointer_y*TILESIZE+9,TILESIZE+2,TILESIZE+2), 2)

	# Draw text
	label = myfont.render("N = New graph | E = New Endpoints | U = Uniform Cost | A = A* Search | W = Weighted A* | V = Visited | S = Save | L = Load", 1, (0,0,0))
	DISPLAYSURF.blit(label, (20, TILESIZE*NUM_ROW+14))

	label = myfont.render("Q = Sequential | I = Integrated | H = " + str(heur[hType]), 1, (0,0,0))
	DISPLAYSURF.blit(label, (20, TILESIZE*NUM_ROW+30))

	label = myfont.render("Cell: ("+str(pointer_x)+","+str(pointer_y)+")", 1, (0,0,0))
	DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 30))

	label = myfont.render("Type: "+graph[pointer_x][pointer_y], 1, (0,0,0))
	DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 50))


	label = myfont.render("Start: ("+str(start_x)+","+str(start_y)+")", 1, (0,0,0))
	DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 80))
	label = myfont.render("Goal: ("+str(goal_x)+","+str(goal_y)+")", 1, (0,0,0))
	DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 100))

	if pathcost != 0:
		label = myfont.render("Path Cost:", 1, (0,0,0))
		DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 130))
		label = myfont.render(str(pathcost), 1, (0,0,0))
		DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 150))

	if pathcost != 0:
		label = myfont.render("Nodes Expanded:", 1, (0,0,0))
		DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 170))
		label = myfont.render(str(nodes_expanded), 1, (0,0,0))
		DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 190))

	if (pointer_x,pointer_y) in fn_f:
		label = myfont.render("f: "+str(fn_f[(pointer_x,pointer_y)]), 1, (0,0,0))
		DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 220))

	if (pointer_x,pointer_y) in fn_g:
		label = myfont.render("g: "+str(fn_g[(pointer_x,pointer_y)]), 1, (0,0,0))
		DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 240))

	if (pointer_x,pointer_y) in fn_h:
		label = myfont.render("h: "+str(fn_h[(pointer_x,pointer_y)]), 1, (0,0,0))
		DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 260))

	label = myfont.render("Time: ", 1, (0,0,0))
	DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 290))
	label = myfont.render(str(elapsedtime*1000)+" ms", 1, (0,0,0))
	DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 310))

	label = myfont.render("Mem: " + str(mem), 1, (0,0,0))
	DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30,340))


	label = myfont.render("Neighbors:", 1, (0,0,0))
	DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, 370))

	draw_y = 390
	neighbors = get_neighbers(pointer_x,pointer_y)

	for neighbor in neighbors:
		label = myfont.render("("+str(neighbor[0])+","+str(neighbor[1])+")", 1, (0,0,0))
		DISPLAYSURF.blit(label, (10+TILESIZE*NUM_COL+30, draw_y))
		draw_y += 20

	# Draw Final Path and Closed List
	if mode == 1:
		for cell in closed_list:
			pygame.draw.circle(DISPLAYSURF, (0,255,0), (cell[0]*TILESIZE+TILESIZE/2+10,cell[1]*TILESIZE+TILESIZE/2+10),TILESIZE/4, 0)
	for cell in path:
		pygame.draw.circle(DISPLAYSURF, (255,0,0), (cell[0]*TILESIZE+TILESIZE/2+10,cell[1]*TILESIZE+TILESIZE/2+10),TILESIZE/4, 0)

	pygame.display.update()

# Get neighbors of a cell
def get_neighbers(x,y):
	myneighbors = [(x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1)]
	myneighbors[:] = [neighbor for neighbor in myneighbors if neighbor[0]>=0 and neighbor[1]>=0 and neighbor[0]<NUM_COL and neighbor[1]<NUM_ROW and graph[neighbor[0]][neighbor[1]] != '0']

	return myneighbors

def cost(currx, curry, nextx, nexty):
	cost = 0.0

	if (graph[currx][curry] == 'a' or graph[currx][curry] == '1') and (graph[nextx][nexty] == 'a' or graph[nextx][nexty] == '1'):
		if((currx == nextx - 1 or currx == nextx + 1) and (curry == nexty - 1 or curry == nexty + 1)):
			#traversing unblocked diagonally
			cost = math.sqrt(2)
		else:
			#traversing unblocked diagonally
			cost = 1
	if (graph[currx][curry] == 'b' or graph[currx][curry] == '2') and (graph[nextx][nexty] == '2' or graph[nextx][nexty] == 'b'):
		if((currx == nextx - 1 or currx == nextx + 1) and (curry == nexty - 1 or curry == nexty + 1)):
			#traversing unblocked diagonally
			cost = math.sqrt(8)
		else:
			#traversing unblocked diagonally
			cost = 2
	if (graph[currx][curry] == 'a' or graph[currx][curry] == '1') and (graph[nextx][nexty] == '2' or graph[nextx][nexty] == 'b'):
		if((currx == nextx - 1 or currx == nextx + 1) and (curry == nexty - 1 or curry == nexty + 1)):
			#traversing unblocked diagonally
			cost = (math.sqrt(2) + math.sqrt(8)) / 2
		else:
			#traversing unblocked diagonally
			cost = 1.5
	if (graph[currx][curry] == '2' or graph[currx][curry] == 'b') and (graph[nextx][nexty] == '1' or graph[nextx][nexty] == 'a'):
		if((currx == nextx - 1 or currx == nextx + 1) and (curry == nexty - 1 or curry == nexty + 1)):
			#traversing unblocked diagonally
			cost = (math.sqrt(2) + math.sqrt(8)) / 2
		else:
			#traversing unblocked diagonally
			cost = 1.5
	if (graph[currx][curry] == 'a' or graph[currx][curry] == 'b') and (graph[nextx][nexty] == 'a' or graph[nextx][nexty] == 'b') and (((currx == nextx + 1 or currx == nexty - 1) and curry == nexty) or ((curry == nexty + 1 or curry == nexty - 1) and currx == nextx)):
		cost = cost / 4
		return cost
	if cost == 0.0:
		print "Could not find cost value. Current: " + str(currx) + ", " + str(curry) + " of type: " + graph[currx][curry] + "/Next: " + str(nextx) + ", " + str(nexty) + " of type: " + graph[nextx][nexty]


	return cost

# A* Stuff

class Points:
	def __init__(self, x, y, parent):
		self.x = x
		self.y = y
		self.parent = parent

	def get_x(self):
		return self.x

	def get_y(self):
		return self.y

	def get_parent(self):
		return self.parent

class Queue:
	def __init__(self):
		self.elements = []

	def empty(self):
		return len(self.elements) == 0

	def put(self, priority, item):
		heapq.heappush(self.elements, (priority, item))

	def get(self):
		return heapq.heappop(self.elements)[1]

	def getPriority(self):
		return heapq.heappop(self.elements)[0]

	def getFull(self):
		if self.empty() == False:
			return heapq.heappop(self.elements)
		return -1

	def remove(self, item):
		if item in self.elements:
			self.elements.remove(item)
			heapq.heapify(self.elements)
			return 0
		return -1

#(priority, item)
#put(priority, item)
class AStarSearch(object):
	def Search(self, startx, starty, goalx, goaly, choice):
		fringe = Queue()
		start = Points(startx, starty, None)
		goal = (goalx, goaly)
		fringe.put(0, start)

		closed_list = {}
		cost_added = {}
		final_path = []
		heuristic_list = {}
		priority_list = {}
		closed_list[(start.get_x(),start.get_y())] = None
		cost_added[(start.get_x(),start.get_y())] = 0

		while not fringe.empty():
			current = fringe.get()
			if (current.get_x(),current.get_y()) == goal:
				print "Made it to goal at " + str(goal[0]) + "," + str(goal[1])

				# Make a straight path from goal to start
				PathNode = current

				while PathNode != None:
					final_path.append((PathNode.get_x(),PathNode.get_y()))
					PathNode = PathNode.get_parent()

				break

			for next in get_neighbers(current.get_x(), current.get_y()):
				new_cost = cost_added[(current.get_x(),current.get_y())] + cost(current.get_x(), current.get_y(), next[0], next[1])

				if next not in cost_added or new_cost < cost_added[next]:
				#if next not in closed_list or new_cost < cost_added[next]:
					cost_added[next] = new_cost		# g
					myheuristic = self.heuristic(next[0], next[1], goal_x, goal_y, choice)
					priority = new_cost + myheuristic
					heuristic_list[next] = myheuristic
					priority_list[next] = priority
					fringe.put(priority, Points(next[0],next[1],current))
					closed_list[next] = current

		mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
		return closed_list, cost_added, final_path, cost_added[(goalx,goaly)], priority_list, heuristic_list, mem

	def heuristic(self,startx,starty,goalx,goaly,hType):
		start = (startx, starty)
		goal = (goalx, goaly)
		hType = int(hType)

		if hType == 1: #manhattan
				heuristic = abs(int(startx) - int(goalx)) + abs(int(starty) - int(goaly))
				heuristic *= 2 #tie-breaker by multiplying the heuristic by (minimum cost)/(max possible path length)
				return heuristic*0.25
		if hType == 2: #euclidean
				heuristic = math.sqrt(((int(startx) - int(goalx)) ** 2) + ((int(starty) - int(goaly)) ** 2))
				heuristic *= 2 #tie-breaker by multiplying the heuristic by (minimum cost)/(max possible path length)
				return heuristic
		if hType == 3: #octile
				dx = abs(int(startx) - int(goalx))
				dy = abs(int(starty) - int(goaly))
				heuristic = (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)
				heuristic *= 2 #tie-breaker by multiplying the heuristic by (minimum cost)/(max possible path length)
				return heuristic
		if hType == 4: #Chebyshev
				heuristic = max(abs(startx - goalx), abs(starty - goaly))
				heuristic *= 2
				return heuristic
		if hType == 5: #5th heuristic
				heuristic = math.sqrt(2)*min(abs(startx - goalx), abs(starty - goaly)) + max(abs(startx - goalx), abs(starty - goaly)) - min(abs(startx - goalx), abs(starty - goaly))
				heuristic *= 2
				return heuristic
		if hType == 6: #Best - minimum of all
				dx = abs(int(startx) - int(goalx))
				dy = abs(int(starty) - int(goaly))
				h1 = dx + dy
				h2 = math.sqrt(((int(startx) - int(goalx)) ** 2) + ((int(starty) - int(goaly)) ** 2))
				h3 = (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)
				h4 = max(dx, dy)
				h5 = math.sqrt(2)*min(dx, dy) + max(dx, dy) - min(dx, dy)
				h6 = min(h1, h2, h3, h4, h5)
				h6 *= 2
				return h6
		return 0

class UniformCostSearch(AStarSearch):
	def Search(self,startx, starty, goalx, goaly):
		return super(UniformCostSearch, self).Search(startx,starty,goalx,goaly,1)
	def heuristic(self,startx, starty, goalx, goaly, choice):
		return 1

class WeightedAStarSearch(AStarSearch):
	def __init__(self,weight):
		self.weight = weight
	def heuristic(self,startx, starty, goalx, goaly, choice):
		return super(WeightedAStarSearch, self).heuristic(startx,starty,goalx,goaly,choice) * float(self.weight)


#Phase 2 Begin
class SequentialAStarSearch(AStarSearch):
	def Search(self,startx, starty, goalx, goaly):
		fringe = [Queue() for x in range(5)]
		start = Points(startx, starty, None)
		goal = (goalx, goaly)

		closed_list = [dict() for y in range (0,5)]
		cost_added = [dict() for y in range (0,5)]
		heuristic_list = [dict() for y in range(0,5)]
		final_path = []
		priority_list = [dict() for y in range(0,5)]
		w2 = 2#weight
		path_cost = 0
	
		for i in range(0, 5):
			closed_list[i] = {}
			cost_added[i] = {}
			heuristic_list[i] = {}
			for next in get_neighbers(start.get_x(), start.get_y()):
			
				new_cost = cost(start.get_x(), start.get_y(), next[0], next[1])
				if next not in cost_added[i] or new_cost < cost_added[i][next]:
					#if next not in closed_list or new_cost < cost_added[next]:
					cost_added[i][next] = new_cost		# g
					myheuristic = self.heuristic(next[0], next[1], goal_x, goal_y, i+1)
					priority = new_cost + myheuristic
					heuristic_list[i][next] = myheuristic
					priority_list[i][next] = priority
					fringe[i].put(priority, Points(next[0],next[1],start))
					closed_list[i][next] = start
			closed_list[i][(start.get_x(), start.get_y())] = None
			cost_added[i][(start.get_x(), start.get_y())] = 0
			cost_added[i][(goalx, goaly)] = float("inf")

		anchor = fringe[0].getFull()
		while not fringe[0].empty():
			for i in range(1, 5):
				#anchor is a tuple (priority, item)

				temp = fringe[i].getFull() #temp is a tuple (item, priority)

				if temp != -1 and temp[0] <= w2*anchor[0]: #main condition

					if temp[1].get_x() == goalx and temp[1].get_y() == goaly:
							# Found goal, return path
							print "Made it to goal at " + str(goal[0]) + "," + str(goal[1])
							path_cost = 0
							# Make a straight path from goal to start
							PathNode = temp[1]
							old_x = PathNode.get_x()
							old_y = PathNode.get_y()
							final_path.append((old_x,old_y))
							PathNode = PathNode.get_parent()

							while PathNode != None:
								path_cost += cost(PathNode.get_x(),PathNode.get_y(),old_x,old_y)
								final_path.append((PathNode.get_x(),PathNode.get_y()))
								old_x = PathNode.get_x()
								old_y = PathNode.get_y()
								PathNode = PathNode.get_parent()

							mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
							return closed_list, cost_added, final_path, path_cost, priority_list, heuristic_list, mem
					else:

						for next in get_neighbers(temp[1].get_x(), temp[1].get_y()):

							new_cost = cost_added[i][(temp[1].get_x(),temp[1].get_y())] + cost(temp[1].get_x(), temp[1].get_y(), next[0], next[1])

							if next not in cost_added[i] or new_cost < cost_added[i][next]:

								#if next not in closed_list or new_cost < cost_added[next]:
								cost_added[i][next] = new_cost		# g
								myheuristic = self.heuristic(next[0], next[1], goalx, goaly, i+1)
								priority = new_cost + myheuristic
								heuristic_list[i][next] = myheuristic
								priority_list[i][next] = priority
								fringe[i].put(priority, Points(next[0],next[1],temp[1]))
								closed_list[i][next] = temp[1]

				else:
					
					if anchor[1].get_x() == goalx and anchor[1].get_y() == goaly:
							# Found goal, return path
							print "Made it to goal at " + str(goal[0]) + "," + str(goal[1])
							path_cost = 0
							# Make a straight path from goal to start
							PathNode = anchor[1]
							old_x = PathNode.get_x()
							old_y = PathNode.get_y()
							final_path.append((old_x,old_y))
							PathNode = PathNode.get_parent()

							while PathNode != None:
								path_cost += cost(PathNode.get_x(),PathNode.get_y(),old_x,old_y)
								final_path.append((PathNode.get_x(),PathNode.get_y()))
								
								old_x = PathNode.get_x()
								old_y = PathNode.get_y()
								PathNode = PathNode.get_parent()

							mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
							return closed_list, cost_added, final_path, path_cost, priority_list, heuristic_list, mem
					else:
						
						for next in get_neighbers(anchor[1].get_x(), anchor[1].get_y()):
							
							new_cost=cost_added[0][(anchor[1].get_x(), anchor[1].get_y())]+cost(anchor[1].get_x(),anchor[1].get_y(),next[0],next[1])

							if next not in cost_added[0] or new_cost < cost_added[0][next]:
								
							#if next not in closed_list or new_cost < cost_added[next]:
								cost_added[0][next] = new_cost		# g
								myheuristic = self.heuristic(next[0], next[1], goalx, goaly, 1)
								priority = new_cost + myheuristic
								heuristic_list[0][next] = myheuristic
								priority_list[0][next] = priority
								fringe[0].put(priority, Points(next[0],next[1],anchor[1]))
								closed_list[0][next] = anchor[1]
					anchor = fringe[0].getFull()

		mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
		return closed_list, cost_added, final_path, path_cost, priority_list, heuristic_list, mem

class IntegratedAStarSearch(AStarSearch):
	def Search(self,startx, starty, goalx, goaly):
		fringe = [Queue() for x in range(5)]
		start = Points(startx, starty, None)
		goal = (goalx, goaly)

		closed_list = {}
		closed_list_anchor = {}
		cost_added = {}
		heuristic_list = [dict() for y in range(0,5)]
		final_path = []
		priority_list = [dict() for y in range(0,5)]
		w2 = 2 # weight
		path_cost = 0

		for i in range(0, 5):
			heuristic_list[i] = {}
			for next in get_neighbers(start.get_x(), start.get_y()):
				
				new_cost = cost(start.get_x(), start.get_y(), next[0], next[1])
				if next not in cost_added or new_cost < cost_added[next]:
					#if next not in closed_list or new_cost < cost_added[next]:
					cost_added[next] = new_cost		# g
					myheuristic = self.heuristic(next[0], next[1], goal_x, goal_y, i+1)
					priority = new_cost + myheuristic
					heuristic_list[i][next] = myheuristic
					priority_list[i][next] = priority
					fringe[i].put(priority, Points(next[0],next[1],start))
					closed_list[next] = start

		closed_list[(start.get_x(), start.get_y())] = None
		closed_list_anchor[(start.get_x(), start.get_y())] = None

		cost_added[(start.get_x(), start.get_y())] = 0
		cost_added[(goalx, goaly)] = float("inf")

		anchor = fringe[0].getFull()
		while not fringe[0].empty():
			for i in range(1, 5):
				#anchor is a tuple (priority, item)

				temp = fringe[i].getFull() #temp is a tuple (item, priority)

				if temp != -1 and temp[0] <= w2*anchor[0]: #main condition

					if temp[1].get_x() == goalx and temp[1].get_y() == goaly:
							# Found goal, return path
							print "Made it to goal at " + str(goal[0]) + "," + str(goal[1])
							path_cost = 0
							# Make a straight path from goal to start
							PathNode = temp[1]
							old_x = PathNode.get_x()
							old_y = PathNode.get_y()
							final_path.append((old_x,old_y))
							PathNode = PathNode.get_parent()

							while PathNode != None:
								path_cost += cost(PathNode.get_x(),PathNode.get_y(),old_x,old_y)
								final_path.append((PathNode.get_x(),PathNode.get_y()))
								
								old_x = PathNode.get_x()
								old_y = PathNode.get_y()
								PathNode = PathNode.get_parent()


							mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
							return [closed_list,closed_list_anchor], cost_added, final_path, path_cost, priority_list, heuristic_list, mem
					else:

						for j in range(1,5):
							fringe[j].remove(temp[1])

						# Expand
						for next in get_neighbers(temp[1].get_x(), temp[1].get_y()):

							new_cost = cost_added[(temp[1].get_x(),temp[1].get_y())] + cost(temp[1].get_x(), temp[1].get_y(), next[0], next[1])

							if next not in cost_added or new_cost < cost_added[next]:

								#if next not in closed_list or new_cost < cost_added[next]:
								cost_added[next] = new_cost		# g
								if next not in closed_list_anchor:
									myheuristic = self.heuristic(next[0], next[1], goalx, goaly, 0)
									priority0 = new_cost + myheuristic
									heuristic_list[0][next] = myheuristic
									priority_list[0][next] = priority0
									fringe[0].put(priority0, Points(next[0],next[1],temp[1]))

									if next not in closed_list:
										for j in range(1,5):
											myheuristic = self.heuristic(next[0], next[1], goalx, goaly, i+1)
											priority = new_cost + myheuristic
											if priority <= w2 * priority0:
												heuristic_list[i][next] = myheuristic
												priority_list[i][next] = priority
												fringe[i].put(priority, Points(next[0],next[1],temp[1]))
												closed_list[next] = temp[1]

				else:
					
					if anchor[1].get_x() == goalx and anchor[1].get_y() == goaly:
							# Found goal, return path
							print "Made it to goal at " + str(goal[0]) + "," + str(goal[1])
							path_cost = 0
							# Make a straight path from goal to start
							PathNode = anchor[1]
							old_x = PathNode.get_x()
							old_y = PathNode.get_y()
							final_path.append((old_x,old_y))
							PathNode = PathNode.get_parent()

							while PathNode != None:
								path_cost += cost(PathNode.get_x(),PathNode.get_y(),old_x,old_y)
								final_path.append((PathNode.get_x(),PathNode.get_y()))
								
								old_x = PathNode.get_x()
								old_y = PathNode.get_y()
								PathNode = PathNode.get_parent()

							mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
							return [closed_list,closed_list_anchor], cost_added, final_path, path_cost, priority_list, heuristic_list, mem
					else:
						
						for j in range(1,5):
							fringe[j].remove(anchor[1])

						# Expand
						for next in get_neighbers(anchor[1].get_x(), anchor[1].get_y()):
							
							new_cost = cost_added[(anchor[1].get_x(),anchor[1].get_y())] + cost(anchor[1].get_x(), anchor[1].get_y(), next[0], next[1])

							if next not in cost_added or new_cost < cost_added[next]:

								#if next not in closed_list or new_cost < cost_added[next]:
								cost_added[next] = new_cost		# g
								if next not in closed_list_anchor:
									myheuristic = self.heuristic(next[0], next[1], goalx, goaly, 0)
									priority0 = new_cost + myheuristic
									heuristic_list[0][next] = myheuristic
									priority_list[0][next] = priority0
									fringe[0].put(priority0, Points(next[0],next[1],anchor[1]))
									closed_list_anchor[next] = anchor[1]
									if next not in closed_list:
										for j in range(1,5):
											myheuristic = self.heuristic(next[0], next[1], goalx, goaly, i+1)
											priority = new_cost + myheuristic
											if priority <= w2 * priority0:
												heuristic_list[i][next] = myheuristic
												priority_list[i][next] = priority
												fringe[i].put(priority, Points(next[0],next[1],anchor[1]))
												closed_list_anchor[next] = anchor[1]
					anchor = fringe[0].getFull()

		mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
		return closed_list, cost_added, final_path, path_cost, priority_list, heuristic_list, mem

# Main loop
running = True

graphSurface = pygame.Surface(DISPLAYSURF.get_size())

areacoordinates = generate_graph()
graphSurface = draw(graphSurface)
start_x,start_y,goal_x,goal_y = generate_endpoints()
final_path = []
closed_list = []
cell_costs = []
priority_list = []
heuristic_list = []
path_cost = 0
elapsed_time = 0
drawmode = 0
nodes_expanded = 0
mapNum = 2;

MySearch = AStarSearch() # Initialize Object

while(running):
	# Get Input
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False
			elif event.key == pygame.K_n:
				graph = [['1' for y in range(NUM_ROW)] for x in range(NUM_COL)]
				areacoordinates = generate_graph()
				graphSurface = draw(graphSurface)
				start_x,start_y,goal_x,goal_y = generate_endpoints()
				final_path = []
				closed_list = []
				priority_list = []
				heuristic_list = []
				cell_costs = []
				path_cost = 0
				elapsed_time = 0
				nodes_expanded = 0
				print "Generated new map"
			elif event.key == pygame.K_e:
				start_x,start_y,goal_x,goal_y = generate_endpoints()
				final_path = []
				closed_list = []
				priority_list = []
				heuristic_list = []
				cell_costs = []
				path_cost = 0
				elapsed_time = 0
				nodes_expanded = 0
				print "Generated new start and finish points"
			elif event.key == pygame.K_s:
				# Save map: get filename
				filename = raw_input("Save map named: ")
				with open(os.path.join("./gen",filename),"w") as mapfile:
					mapfile.write(str((start_x,start_y)))		# Write start
					mapfile.write("\n")
					mapfile.write(str((goal_x,goal_y)))			# Write goal
					mapfile.write("\n")

					for area in areacoordinates:				# Write hard to traverse area centers
						mapfile.write(str((area[0],area[1])))
						mapfile.write("\n")

					for y in range(len(graph[x])):				# Write each cell
						for x in range(len(graph)):
							mapfile.write(str(graph[x][y]))
						mapfile.write("\n")

					mapfile.close()
				print "Map saved!"
			elif event.key == pygame.K_l:
				# Load map: get filename
				filename = raw_input("Load map named: ")
				with open(os.path.join("./gen",filename),"r") as mapfile: #changed to allow using /maps folder
					new_start = make_tuple(mapfile.readline())
					start_x = new_start[0]
					start_y = new_start[1]
					new_goal = make_tuple(mapfile.readline())
					goal_x = new_goal[0]
					goal_y = new_goal[1]

					areacoordinates = []

					for i in range(8):
						new_area = make_tuple(mapfile.readline())
						areacoordinates.append((new_area[0],new_area[1]))

					for y in range(len(graph[x])):				# Read each cell
						for x in range(len(graph)):
							graph[x][y] = mapfile.read(1)
						mapfile.read(1)

					mapfile.close()
				final_path = []
				closed_list = []
				cell_costs = []
				priority_list = []
				heuristic_list = []
				path_cost = 0
				elapsed_time = 0
				nodes_expanded = 0
				graphSurface = draw(graphSurface)
				print "Map loaded!"
			elif event.key == pygame.K_UP:
				if pointer_y-1 >= 0:
					pointer_y -= 1
			elif event.key == pygame.K_LEFT:
				if pointer_x-1 >= 0:
					pointer_x -= 1
			elif event.key == pygame.K_RIGHT:
				if pointer_x+1 < NUM_COL:
					pointer_x += 1
			elif event.key == pygame.K_DOWN:
				if pointer_y+1 < NUM_ROW:
					pointer_y += 1
			elif event.key == pygame.K_v:
				# draw closed list
				if drawmode == 0:
					drawmode = 1
				else:
					drawmode = 0
			elif event.key == pygame.K_h:
				if hType > 5:
					hType = 1
				else:
					hType = hType + 1
			elif event.key == pygame.K_a:		# -------- A* Search --------
				MySearch = AStarSearch()
				start_time = time.time()
				closed_list, cell_costs, final_path, path_cost, priority_list, heuristic_list,mem = MySearch.Search(start_x, start_y, goal_x, goal_y,hType)
				elapsed_time = time.time() - start_time
				nodes_expanded = len(closed_list)
			elif event.key == pygame.K_u:		# -------- Uniform Cost Search --------
				MySearch = UniformCostSearch()
				start_time = time.time()
				closed_list, cell_costs, final_path, path_cost, priority_list, heuristic_list,mem = MySearch.Search(start_x, start_y, goal_x, goal_y)
				elapsed_time = time.time() - start_time
				nodes_expanded = len(closed_list)
			elif event.key == pygame.K_w:		# -------- Weighted A* Search --------
				weight = 0 #weight of heuristic

				while float(weight) < 1:
					weight = raw_input("Enter a weight for your search: ")

				MySearch = WeightedAStarSearch(weight)
				start_time = time.time()
				closed_list, cell_costs, final_path, path_cost, priority_list, heuristic_list,mem = MySearch.Search(start_x, start_y, goal_x, goal_y, hType)
				elapsed_time = time.time() - start_time

				nodes_expanded = len(closed_list)
			elif event.key == pygame.K_q:		# -------- Sequential A* Search --------
				#sequential search goes here
				print "Sequential Search"
				MySearch = SequentialAStarSearch()
				start_time = time.time()
				closed_lists, cell_costs, final_path, path_cost, priority_list, heuristic_list,mem = MySearch.Search(start_x,start_y,goal_x, goal_y)
				elapsed_time = time.time() - start_time

				closed_list = []
				# Combine closed lists
				for list in closed_lists:
					for cell in list:
						if cell not in closed_list:
							closed_list.append(cell)
				nodes_expanded = len(closed_list)

			elif event.key == pygame.K_i:		# -------- Integrated A* Search --------
				#integrated search goes here
				print "Integrated Search"
				MySearch = IntegratedAStarSearch()
				start_time = time.time()
				closed_lists, cell_costs, final_path, path_cost, priority_list, heuristic_list,mem = MySearch.Search(start_x,start_y,goal_x, goal_y)
				elapsed_time = time.time() - start_time

				closed_list = []
				# Combine closed lists
				for list in closed_lists:
					for cell in list:
						if cell not in closed_list:
							closed_list.append(cell)
				nodes_expanded = len(closed_list)

			elif event.key == pygame.K_d:
				fo = open("diagnostics"+str(mapNum)+".txt", "w")

				for num in range (1, 11):
					print "x is " + str(x)
					if num < 10:
						filename = "map"+str(mapNum)+"_0"+str(num)
						print "filenam is: " + filename #change map prefix to match the series
					if num == 10:
						filename = "map"+str(mapNum)+"_10" #change here too
						print "filenam is: " + filename #
					with open(os.path.join("./gen",filename),"r") as mapfile: #changed to allow using /maps folder
						new_start = make_tuple(mapfile.readline())
						start_x = new_start[0]
						start_y = new_start[1]
						new_goal = make_tuple(mapfile.readline())
						goal_x = new_goal[0]
						goal_y = new_goal[1]

						areacoordinates = []
						for i in range(8):
							new_area = make_tuple(mapfile.readline())
							areacoordinates.append((new_area[0],new_area[1]))

						for y in range(len(graph[x])):				# Read each cell
							for x in range(len(graph)):
								graph[x][y] = mapfile.read(1)
							mapfile.read(1)
						mapfile.close()
					final_path = []
					closed_list = []
					cell_costs = []
					priority_list = []
					heuristic_list = []
					path_cost = 0
					elapsed_time = 0
					nodes_expanded = 0
					graphSurface = draw(graphSurface)

					print "Performing UCS on map: " + filename
					MySearch = UniformCostSearch()
					start_time = time.time()
					closed_list, cell_costs, final_path, path_cost, priority_list, heuristic_list, mem = MySearch.Search(start_x, start_y, goal_x, goal_y)
					elapsed_time = time.time() - start_time
					fo.write(str(filename) + "\t" + "UCS" + "\t(None)\t" + str(elapsed_time*1000) + "\t" + str(path_cost) + "\t" + str(len(closed_list)) + "\t" + str(mem + (4*len(closed_list))) + "\t" + str(mem) + "\n")


					for choice in range(1, 6):
						print "Performing A* on map: " + str(filename) + " with Heuristic: " + str(choice)
						MySearch = AStarSearch()
						start_time = time.time()
						closed_list, cell_costs, final_path, path_cost, priority_list, heuristic_list, mem = MySearch.Search(start_x, start_y, goal_x, goal_y, choice)
						elapsed_time = time.time() - start_time
						fo.write(str(filename) + "\t" + "A* " + "\t" + str(choice) + "\t" + str(elapsed_time*1000) + "\t" + str(path_cost) + "\t" + str(len(closed_list)) + "\t" + str(mem + (4*len(closed_list))) + "\t" + str(mem))
						fo.write("\n")

					weight = 1.25
					for choice in range (1, 6):
					    print "Performing Weighted A* on map: " + filename + " with Heuristic: " + str(choice) + " and weight " + str(weight)
					    MySearch = WeightedAStarSearch(weight)
					    start_time = time.time()
					    closed_list, cell_costs, final_path, path_cost, priority_list, heuristic_list, mem = MySearch.Search(start_x, start_y, goal_x, goal_y, choice)
					    elapsed_time = time.time() - start_time
					    fo.write(str(filename) + "\t" + "A* (Weight " + str(weight) + ")" + "\t" + str(choice) + "\t" + str(elapsed_time*1000) + "\t" + str(path_cost) + "\t" + str(len(closed_list)) + "\t" + str(mem + (4*len(closed_list))) + "\t" + str(mem))
					    fo.write("\n")
					weight = 2
					for choice in range (1, 6):
					    print "Performing Weighted A* on map: " + filename + " with Heuristic: " + str(choice) + " and weight " + str(weight)
					    MySearch = WeightedAStarSearch(weight)
					    start_time = time.time()
					    closed_list, cell_costs, final_path, path_cost, priority_list, heuristic_list, mem = MySearch.Search(start_x, start_y, goal_x, goal_y, choice)
					    elapsed_time = time.time() - start_time
					    fo.write(str(filename) + "\t" + "A* (Weight " + str(weight) + ")\t" + str(choice) + "\t" + str(elapsed_time*1000) + "\t" + str(path_cost) + "\t" + str(len(closed_list)) + "\t" + str(mem + (4*len(closed_list))) + "\t" + str(mem))
					    fo.write("\n")

					print "Performing Sequential A* on map: " + filename
					mySearch = SequentialAStarSearch()
					start_time = time.time()
					closed_lists, cell_costs, final_path, path_cost, priority_list, heuristic_list, mem = mySearch.Search(start_x,start_y,goal_x, goal_y)
					elapsed_time = time.time() - start_time
					closed_list = []
					for list in closed_lists:
						for cell in list:
							if cell not in closed_list:
								closed_list.append(cell)
					nodes_expanded = len(closed_list)
					fo.write(str(filename) + "\t" + "Sequential Heuristics A*" + "\t(All)\t" + "\t" + str(elapsed_time*1000) + "\t" + str(path_cost) + "\t" + str(len(closed_list)) + "\t" + str(mem + (4*len(closed_list))) + "\t" + str(mem))
					fo.write("\n")

					print "Integrated Search"
					MySearch = IntegratedAStarSearch()
					start_time = time.time()
					closed_lists, cell_costs, final_path, path_cost, priority_list, heuristic_list, mem = MySearch.Search(start_x,start_y,goal_x, goal_y)
					elapsed_time = time.time() - start_time
					closed_list = []
					# Combine closed lists
					for list in closed_lists:
						for cell in list:
							if cell not in closed_list:
								closed_list.append(cell)
					nodes_expanded = len(closed_list)
					fo.write(str(filename) + "\t" + "Integrated Heuristics A*" + "\t(All)\t" + str(elapsed_time*1000) + "\t" + str(path_cost) + "\t" + str(len(closed_list)) + "\t" + str(mem + (4*len(closed_list))) + "\t" + str(mem))
					fo.write("\n")
				fo.close()
				mapNum += 1




		draw_ui(graphSurface,closed_list,final_path,path_cost,nodes_expanded,drawmode,elapsed_time,cell_costs, priority_list, heuristic_list)

pygame.quit()