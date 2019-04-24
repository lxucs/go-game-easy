#!/usr/bin/env python
# coding: utf-8

"""Go library made with pure Python.

This library offers a variety of Go related classes and methods.

There is a companion module called 'goban' which serves as a front-end
for this library, forming a fully working go board together.

"""

__author__ = "Aku Kotkavuo <aku@hibana.net>"
__version__ = "0.1"
import pygame
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
'''class action:
    def __init__(self,point,color):
        self.point=point
        self.color=color'''
def opponentcolor(color):
    if color=='WHITE':
        return 'BLACK'
    elif color =='BLACK':
        return 'WHITE'
    else:
        print('invalid color: '+str(color))
        return KeyError

def neighbors(point):
    """Return a list of neighboring points."""
    neighboring = [(point[0] - 1, point[1]),
                   (point[0] + 1, point[1]),
                   (point[0], point[1] - 1),
                   (point[0], point[1] + 1)]
    for point in neighboring:
        if not 0 < point[0] < 20 or not 0 < point[1] < 20:
            neighboring.remove(point)
    return neighboring  



def calliberty(points,board):
        """Find and return the liberties of the point."""
        liberties = neighbors(points)
        liberties=list(filter(lambda point: not( board.stonedict['BLACK'][point] or board.stonedict['WHITE'][point] ), liberties))
        return liberties


class Group(object):
    def __init__(self, board, point,color,liberties=None):
        """Create and initialize a new group.

        Arguments:
        board -- the board which this group resides in
        point -- the initial stone in the group

        """
        self.board = board
        if isinstance(point,list): #in process of copying
            self.points=point
            self.liberties=liberties
        else: #create a new group
            self.points=[point]
            self.liberties=calliberty(point,board)
        self.color=color

    '''def merge(self, group, stone):
        """Merge two groups.

        This method merges the argument group with this one by adding
        all its stones into this one. After that it removes the group
        from the board.

        Arguments:
        group -- the group to be merged with this one

        """
        if self.color!=group.color:
            print('different merging colors!')
            raise ValueError
        self.stones.extend(group.stones)
        for point in group.liberties:
            
            
        self.board.groups.remove(group)'''
    @property
    def numliberty(self):
        return len(self.liberties)
    
    def allneighbors(self):
        neighbors = []
        for stone in self.stones:
            neighbors.extend(stone.neighbors())
        return list(set(neighbors))
        
    def remove(self):
        """Remove the entire group."""
        '''self.board.groups[self.color].remove(self)
        self.board.libertydict[self.color].remove(self)
        for point in self.allneighbors():
            for group in self.board.libertydict[opponentcolor(self.color)][point]:
                group.liberty.append(point)
                self.board.libertydict[]'''
        self.board.removedgroup=self
    
    def extendstone(self,point):
        '''update liberty after being extended a stone'''
        for liberty in calliberty(point,self.board):
            if liberty not in self.liberties:
                self.liberties.append(liberty)
                self.board.libertydict[self.color][liberty].append(self)
        self.board.checkendanger(self)
        self.addstones([point])

    def addstones(self,pointlist):
        '''Only update stones, not liberties'''
        self.points.extend(pointlist)
        for point in pointlist:
            self.board.stonedict[self.color][point].append(self)
    
    def shortenliberty(self,point,color):
        self.liberties.remove(point)
        if len(self.liberties)==0 and self.color!=color: #the new stone is opponent's so check winning status
            self.remove()
            self.board.winner=opponentcolor(self.color)
        if len(self.liberties)==1 :
            self.board.endangeredgroup.append(self) #This group only have one liberty now

    def __str__(self):
        """Return a list of the group's stones as a string."""
        return str([str(point) for point in self.points])+' '+self.color
    
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

    def copy(self,newboard):
        return Group(newboard,self.points,self.color,liberties=self.liberties.copy())
    
class Board(object):
    def __init__(self):
        """Create and initialize an empty board."""
        self.groups = {'BLACK':[],'WHITE':[]}
        self.next = 'BLACK'
        self.libertydict={'BLACK':{},'WHITE':{}}
        self.stonedict={'BLACK':{},'WHITE':{}}
        self.winner=None
        self.endangeredgroup=[] #group with only 1 liberty
        for i in range(1,20):
            for j in range(1,20):
                self.libertydict['BLACK'][(i,j)]=[]
                self.libertydict['WHITE'][(i,j)]=[]
                self.stonedict['BLACK'][(i,j)]=[]
                self.stonedict['WHITE'][(i,j)]=[]
                
    def showliberty(self):
        '''show the liberty of each group'''
        result={}
        for point,grouplist in self.libertydict['BLACK'].items():
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
    
    def shortenlibertyforgroups(self,point,color):
        '''remove the liberty for a group in self.libertydict after removing it in the group object'''
        for group in self.libertydict['BLACK'][point]:
            group.shortenliberty(point,color)
        self.libertydict['BLACK'][point]=[]
        for group in self.libertydict['WHITE'][point]:
            group.shortenliberty(point,color)
        self.libertydict['WHITE'][point]=[]
    
    def checkendanger(self,newgroup):
        '''After updating liberties, check if endanger'''
        allliberties=newgroup.liberties
        if newgroup in self.endangeredgroup and len(allliberties)>1:
            self.endangeredgroup.remove(newgroup)
        else:
            if len(allliberties)==1:
                self.endangeredgroup.append(newgroup)
                
    def creategroup(self,point,color):
        newgroup=Group(self,point,color)
        self.groups[color].append(newgroup)
        for liberty in newgroup.liberties:
            self.libertydict[color][liberty].append(newgroup)
        self.stonedict[color][point].append(newgroup)
      
    def removegroup(self,group):
        '''delete every record in self.xxxdict before deleting the group itself'''
        '''used in merge only'''
        color=group.color
        for point in group.points:
            self.stonedict[color][point].remove(group)
        for liberty in group.liberties:
            self.libertydict[color][liberty].remove(group)
        self.groups[group.color].remove(group)
        if len(group.liberties)<=1:
            self.endangeredgroup.remove(group) #no longer endanger after merging

        
    def mergegroups(self,grouplist,point): 
        '''merge every group in grouplist, with stone being the latest move'''
        color=grouplist[0].color
        newgroup=grouplist[0]
        allliberties=grouplist[0].liberties
        newgroup.addstones([point])
        for group in grouplist[1:]:
            allliberties.extend(group.liberties)
            newgroup.addstones(group.points)
            self.removegroup(group)
        
        allliberties=list(set(allliberties).union(set(calliberty(point,self))))
        for point in allliberties:
            if newgroup not in self.libertydict[color][point]:
                self.libertydict[color][point].append(newgroup)
        newgroup.liberties=allliberties
        self.checkendanger(newgroup)
    

    
    def getLegalAction(self):
        endangerflag=set()
        for group in self.endangeredgroup:
            if group.color==self.next:
                endangerflag=endangerflag.union(group.liberties) #you need to save your own group
            else:
                return group.liberties[0] #Return the point directly (not list) to congratulate that you win
        if len(endangerflag)>1:
            return endangerflag #return the set to indicate you lose: you have more than 2 endangered group
        elif len(endangerflag)==1:
            return list(endangerflag)# You must rescue your sole endangerer group in this move
        legalactionset=set()
        for group in self.groups[opponentcolor(self.next)]:
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
        self.shortenlibertyforgroups(point,self.next) # remove the point from all groups's liberty
        print(self.winner,'@@@@')
        if self.winner:
            print(self.winner+' wins!')
            self.next=opponentcolor(self.next)
            return True
        if len(groupintouch)==1: # Update the only group in touch with the new stone
            groupintouch[0].extendstone(point)
        elif len(groupintouch)==0: # Create a group for the new stone
            self.creategroup(point,self.next)
        else: #Merge all the groups in touch with the new stone
            self.mergegroups(groupintouch,point)
        self.next=opponentcolor(self.next) #Take turns
        return True
    
    def generateSuccessorState(self,action):
        newboard=self.copy()
        newboard.putstone(action)
        return newboard
        
    def randommove(self):
        legalmove=self.getLegalAction()
        if isinstance(legalmove,tuple):
            legalmove=[legalmove]
        return list(legalmove)[0]
        
    def __str__(self):
        A='next:'+self.next
        B=self.showliberty()
        C=''
        for group in self.groups['BLACK']:
            C+=str(group)+' '+str(group.liberties)+'\n'
        for group in self.groups['WHITE']:
            C+=str(group)+' '+str(group.liberties)+'\n'
        return A+'\n'+B+'\n'+str(self.endangeredgroup) +'\n'+C
        
        
    def search(self, point):
        '''Too see if a point has been placed on the board'''
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
                    newboard.endangeredgroup.append(copygroup)

    

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