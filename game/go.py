#!/usr/bin/env python
# coding: utf-8

"""Go library made with pure Python.

This library offers a variety of Go related classes and methods.

There is a companion module called 'goban' which serves as a front-end
for this library, forming a fully working go board together.

"""

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BOARD_SIZE = 20  # number of rows/cols = BOARD_SIZE - 1


def opponent_color(color):
    if color == 'WHITE':
        return 'BLACK'
    elif color == 'BLACK':
        return 'WHITE'
    else:
        print('Invalid color: ' + color)
        return KeyError


def neighbors(point):
    """Return a list of neighboring points."""
    neighboring = [(point[0] - 1, point[1]),
                   (point[0] + 1, point[1]),
                   (point[0], point[1] - 1),
                   (point[0], point[1] + 1)]
    return [point for point in neighboring if 0 < point[0] < BOARD_SIZE and 0 < point[1] < BOARD_SIZE]


def cal_liberty(points,board):
    """Find and return the liberties of the point."""
    return [point for point in neighbors(points)
            if not board.stonedict['BLACK'][point] and not board.stonedict['WHITE'][point]]


class Group(object):
    def __init__(self, board, point, color, liberties=None):
        """
        Create and initialize a new group.
        :param board: the board which this group resides in
        :param point: the initial stone in the group
        :param color:
        :param liberties:
        """
        self.board = board
        self.color = color

        if isinstance(point, list):
            self.points = point
            self.liberties = liberties
        else:  # create a new group
            self.points = [point]
            self.liberties = set(cal_liberty(point, board))

    @property
    def num_liberty(self):
        return len(self.liberties)
        
    def remove(self):
        """TODO"""
        self.board.removedgroup=self

    def add_stones(self, pointlist):
        """Only update stones, not liberties"""
        self.points.extend(pointlist)
        for point in pointlist:
            self.board.stonedict[self.color][point].append(self)
    
    def extend_stone(self, point):
        """Update stones and liberties"""
        self.add_stones([point])

        for liberty in cal_liberty(point, self.board):
            if liberty not in self.liberties:
                self.liberties.add(liberty)
                self.board.libertydict[self.color][liberty].append(self)
        self.board.check_endanger(self)  # TODO
    
    def remove_liberty(self, point):
        self.liberties.remove(point)

    def __str__(self):
        """Return a list of the group's stones as a string."""
        return self.color + ' - ' + ', '.join([str(point) for point in self.points])
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        if not hasattr(other,'poinst') or len(self.points)!=len(other.points):
            return False
        for stone1,stone2 in zip(self.points,other.point):
            if stone1!=stone2:
                return False
        return True
    
    def __hash__(self):
        num=0
        for idx,stone in enumerate(self.points):
            num+=hash(stone)*(13**idx)
        return hash(num)

    def copy(self, newboard):
        return Group(newboard, self.points.copy(), self.color, liberties=self.liberties.copy())


class Board(object):
    def __init__(self, initial_color='BLACK'):
        self.winner = None
        self.next = initial_color

        # Point dict
        self.libertydict = {'BLACK': {}, 'WHITE': {}}  # {color: {point: {groups}}}
        self.stonedict = {'BLACK': {}, 'WHITE': {}}

        # Group list
        self.groups = {'BLACK': [], 'WHITE': []}
        self.endangered_groups = []  # groups with only 1 liberty

        for i in range(1, BOARD_SIZE):
            for j in range(1, BOARD_SIZE):
                self.libertydict['BLACK'][(i, j)]=[]
                self.libertydict['WHITE'][(i, j)]=[]
                self.stonedict['BLACK'][(i, j)]=[]
                self.stonedict['WHITE'][(i, j)]=[]

    # TODO
    def print_liberties(self):
        """Show the liberty of each group"""
        result = {}
        for point, grouplist in self.libertydict['BLACK'].items():
            for group in grouplist:
                if str(group) not in result:
                    result[str(group)]=[]
                result[str(group)].append(point)
        for point,grouplist in self.libertydict['WHITE'].items():
            for group in grouplist:
                if str(group) not in result:
                    result[str(group)]=[]
                result[str(group)].append(point)
        resultstr=''
        for groupname,pointlist in result.items():
            resultstr+=groupname+' '+str(pointlist)+'\n'
        return resultstr
    
    def shorten_liberty_for_groups(self, point, color):
        def shorten_liberty(group, point, color):
            """Remove the liberty from given group, update winner or endangered groups"""
            group.remove_liberty(point)
            if len(group.liberties) == 0 and group.color != color:  # The new stone is opponent's, check winning status
                group.remove()
                self.winner = opponent_color(group.color)
            elif len(group.liberties) == 1:  # This group only has one liberty now
                self.endangered_groups.append(group)

        for group in self.libertydict['BLACK'][point]:
            shorten_liberty(group, point, color)
        self.libertydict['BLACK'][point] = []

        for group in self.libertydict['WHITE'][point]:
            shorten_liberty(group, point, color)
        self.libertydict['WHITE'][point] = []
    
    def check_endanger(self, newgroup):
        # TODO
        """After updating liberties, check if endanger"""
        allliberties=newgroup.liberties
        if newgroup in self.endangered_groups and len(allliberties)>1:
            self.endangered_groups.remove(newgroup)
        else:
            if len(allliberties)==1:
                self.endangered_groups.append(newgroup)
                
    def create_group(self, point, color):
        # Update group list
        group = Group(self, point, color)
        self.groups[color].append(group)
        # Update endangered group
        if len(group.liberties) <= 1:
            self.endangered_groups.append(group)
        # Update stonedict
        self.stonedict[color][point].append(group)
        # Update libertydict
        for liberty in group.liberties:
            self.libertydict[color][liberty].append(group)
      
    def remove_group(self, group):
        color = group.color
        # Update group list
        self.groups[group.color].remove(group)
        # Update endangered_groups
        if group in self.endangered_groups:
            self.endangered_groups.remove(group)
        # Update stonedict
        for point in group.points:
            self.stonedict[color][point].remove(group)
        # Update libertydict
        for liberty in group.liberties:
            self.libertydict[color][liberty].remove(group)

    def mergegroups(self,grouplist,point): 
        """Merge every group in grouplist, with stone being the latest move"""
        color=grouplist[0].color
        newgroup=grouplist[0]
        allliberties=grouplist[0].liberties
        newgroup.add_stones([point])
        for group in grouplist[1:]:
            allliberties = allliberties | group.liberties
            newgroup.add_stones(group.points)
            self.remove_group(group)
        
        allliberties=list(set(allliberties).union(set(cal_liberty(point, self))))
        for point in allliberties:
            if newgroup not in self.libertydict[color][point]:
                self.libertydict[color][point].append(newgroup)
        newgroup.liberties=allliberties
        self.check_endanger(newgroup)
    

    def getLegalAction(self):
        endangerflag=set()
        for group in self.endangered_groups:
            if group.color==self.next:
                endangerflag=endangerflag.union(group.liberties) #you need to save your own group
            else:
                return group.liberties[0] #Return the point directly (not list) to congratulate that you win
        if len(endangerflag)>1:
            return endangerflag #return the set to indicate you lose: you have more than 2 endangered group
        elif len(endangerflag)==1:
            return list(endangerflag)# You must rescue your sole endangerer group in this move
        legalactionset=set()
        for group in self.groups[opponent_color(self.next)]:
            legalactionset=legalactionset.union(set(group.liberties))
        return list(legalactionset)
    
    def putstone(self,point,checklegal=False):
        if checklegal:
            legallist=self.getLegalAction()
            if isinstance(legallist,tuple):
                legallist=[legallist]
            if point not in legallist:
                print ('Error: illegal move, try again.')
                return False
        groupintouch=self.libertydict[self.next][point] # find all your group attache to point
        self.shorten_liberty_for_groups(point,self.next) # remove the point from all groups's liberty
        print(self.winner,'@@@@')
        if self.winner:
            print(self.winner+' wins!')
            self.next=opponent_color(self.next)
            return True
        if len(groupintouch)==1: # Update the only group in touch with the new stone
            groupintouch[0].extend_stone(point)
        elif len(groupintouch)==0: # Create a group for the new stone
            self.create_group(point,self.next)
        else: #Merge all the groups in touch with the new stone
            self.mergegroups(groupintouch,point)
        self.next=opponent_color(self.next) #Take turns
        return True
    
    def generate_successor_state(self, action):
        newboard = self.copy()
        newboard.putstone(action)
        return newboard
        
    def random_move(self):
        legalmove=self.getLegalAction()
        if isinstance(legalmove,tuple):
            legalmove=[legalmove]
        return list(legalmove)[0]
        
    def __str__(self):
        A='next:'+self.next
        B=self.print_liberties()
        C=''
        for group in self.groups['BLACK']:
            C+=str(group)+' '+str(group.liberties)+'\n'
        for group in self.groups['WHITE']:
            C+=str(group)+' '+str(group.liberties)+'\n'
        return A+'\n'+B+'\n'+str(self.endangered_groups) +'\n'+C
        
        
    def search(self, point):
        """Too see if a point has been placed on the board"""
        if self.stonedict['BLACK'][point] or self.stonedict['WHITE'][point] :
            return True
        else:
            return False
    
    def copy(self):
        newboard=Board()
        for color in ['BLACK','WHITE']:
            for group in self.groups[color]:
                copygroup=group.copy(newboard)
                newboard.groups[color].append(copygroup)
                for liberty in copygroup.liberties:
                    newboard.libertydict[color][liberty].append(copygroup)
                for point in copygroup.points:
                    newboard.stonedict[color][point].append(copygroup)
                if len(group.liberties)==1:
                    newboard.endangered_groups.append(copygroup)
        return newboard
    

if __name__=='__main__':  
    A=Board()
    A.putstone((10,10))
    A.putstone((9,10))
    A.putstone((9,9))
    A.putstone((8,9))
    A.putstone((9,11))
    A.putstone((8,10))
    A.putstone((8,11))
    print(str(A))