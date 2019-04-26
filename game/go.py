#!/usr/bin/env python
from copy import deepcopy


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
    liberties = [point for point in neighbors(points)
                 if not board.stonedict['BLACK'][point] and not board.stonedict['WHITE'][point]]
    return set(liberties)


class Group(object):
    def __init__(self, point, color, liberties):
        """
        Create and initialize a new group.
        :param point: the initial stone in the group
        :param color:
        :param liberties:
        """
        self.color = color
        if isinstance(point, list):
            self.points = point
        else:
            self.points = [point]
        self.liberties = liberties

    @property
    def num_liberty(self):
        return len(self.liberties)

    def add_stones(self, pointlist):
        """Only update stones, not liberties"""
        self.points.extend(pointlist)
    
    def remove_liberty(self, point):
        self.liberties.remove(point)

    def __str__(self):
        """Summarize color, stones, liberties."""
        return '%s - stones: [%s]; liberties: [%s]' % \
               (self.color,
                ', '.join([str(point) for point in self.points]),
                ', '.join([str(point) for point in self.points]))
    
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


class Board(object):
    """
    get_legal_action(), generate_successor_state() are the external game interface.
    put_stone() is the main internal method that contains all logic to update game state.
    create_group(), remove_group(), merge_groups() operations don't check winner or endangered groups.
    winner or endangered groups are updated in put_stone().
    """
    def __init__(self, initial_color='BLACK'):
        self.winner = None
        self.next = initial_color

        # Point dict
        self.libertydict = {'BLACK': {}, 'WHITE': {}}  # {color: {point: {groups}}}
        self.stonedict = {'BLACK': {}, 'WHITE': {}}

        # Group list
        self.groups = {'BLACK': [], 'WHITE': []}
        self.endangered_groups = []  # groups with only 1 liberty
        self.removed_groups = []  # This is assigned when game ends

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
                
    def create_group(self, point, color):
        """Create a new group."""
        # Update group list
        group = Group(point, color, cal_liberty(point, self))
        self.groups[color].append(group)
        # Update endangered group
        if len(group.liberties) <= 1:
            self.endangered_groups.append(group)
        # Update stonedict
        self.stonedict[color][point].append(group)
        # Update libertydict
        for liberty in group.liberties:
            self.libertydict[color][liberty].append(group)
        return group
      
    def remove_group(self, group):
        """Remove the group."""
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

    def merge_groups(self, grouplist, point):
        """
        Merge groups (assuming same color).
        Called by put_stone(); all groups already have this liberty removed.
        :param grouplist:
        :param point:
        """
        color = grouplist[0].color
        newgroup = grouplist[0]
        all_liberties = grouplist[0].liberties

        # Add last move (update newgroup and stonedict)
        newgroup.add_stones([point])
        self.stonedict[color][point].append(newgroup)
        all_liberties = all_liberties | cal_liberty(point, self)

        # Merge with other groups (update newgroup and stonedict)
        for group in grouplist[1:]:
            newgroup.add_stones(group.points)
            for p in group.points:
                self.stonedict[color][p].append(newgroup)
            all_liberties = all_liberties | group.liberties
            self.remove_group(group)

        # Update newgroup liberties (point is already removed from group liberty)
        newgroup.liberties = all_liberties

        # Update libertydict
        self.libertydict[color][point] = []
        self.libertydict[opponent_color(color)][point] = []
        for point in all_liberties:
            if newgroup not in self.libertydict[color][point]:
                self.libertydict[color][point].append(newgroup)

        return newgroup

    def get_legal_action(self):
        endangered_liberties = set()
        for group in self.endangered_groups:
            if group.color == self.next:
                endangered_liberties = endangered_liberties | group.liberties
            else:
                return group.liberties[0]  # Return the point to indicate you win

        if len(endangered_liberties) > 1:
            return endangered_liberties  # Return the set to indicate you lose

        # No win or lose now; return a list of valid moves
        if len(endangered_liberties) == 1:
            return list(endangered_liberties)  # Must rescue your sole endangered liberty in this move
        legal_actions = set()
        for group in self.groups[opponent_color(self.next)]:
            legal_actions = legal_actions | group.liberties
        return list(legal_actions)

    def shorten_liberty_for_groups(self, point, color):
        """
        Remove the liberty from all belonging groups; update all consequences such as winner or endangered groups.
        :param point:
        :param color:
        :return:
        """
        def shorten_liberty(group, point, color):
            group.remove_liberty(point)
            if len(group.liberties) == 0 and group.color != color:  # The new stone is opponent's, check winning status
                self.removed_groups.append(group)  # Set removed_group
                self.winner = opponent_color(group.color)
            elif len(group.liberties) == 1:  # This group only has one liberty now
                self.endangered_groups.append(group)

        # Check opponent's groups first
        opponent = opponent_color(color)
        for group in self.libertydict[opponent][point]:
            shorten_liberty(group, point, color)
        self.libertydict['BLACK'][point] = []

        # If any opponent's group die, no need to check self group
        if not self.winner:
            for group in self.libertydict['WHITE'][point]:
                shorten_liberty(group, point, color)
        self.libertydict['WHITE'][point] = []
    
    def put_stone(self, point, check_legal=False):
        if check_legal:
            legal_actions = self.get_legal_action()
            if isinstance(legal_actions, tuple):
                legal_actions = [legal_actions]
            if point not in legal_actions:
                print('Error: illegal move, try again.')
                return False

        # Get all self-groups containing this liberty
        self_belonging_groups = self.libertydict[self.next][point]

        # Remove the liberty from all belonging groups (with consequences updated such as winner)
        self.shorten_liberty_for_groups(point, self.next)
        print(self.winner, '@@@@')
        if self.winner:
            print(self.winner + ' wins!')
            self.next = opponent_color(self.next)
            return True

        # Update groups with the new point
        if len(self_belonging_groups) == 0:  # Create a group for the new stone
            new_group = self.create_group(point, self.next)
        else:  # Merge all self-groups in touch with the new stone
            new_group = self.merge_groups(self_belonging_groups, point)

        # Update endangered groups
        if new_group in self.endangered_groups and len(new_group.liberties) > 1:
            self.endangered_groups.remove(new_group)
        elif new_group not in self.endangered_groups and len(new_group.liberties) == 1:
            self.endangered_groups.append(new_group)

        self.next = opponent_color(self.next)
        return True
    
    def generate_successor_state(self, action):
        board = self.copy()
        board.put_stone(action)
        return board
        
    def __str__(self):
        str_groups = [str(group) for group in self.groups['BLACK']] + [str(group) for group in self.groups['WHITE']]
        return 'Next: %s\n%s' % (self.next, '\n'.join(str_groups))

    def exist_stone(self, point):
        """To see if a stone has been placed on the board"""
        return self.stonedict['BLACK'][point] or self.stonedict['WHITE'][point]

    def copy(self):
        return deepcopy(self)
    

if __name__=='__main__':  
    A=Board()
    A.put_stone((10,10))
    A.put_stone((9,10))
    A.put_stone((9,9))
    A.put_stone((8,9))
    A.put_stone((9,11))
    A.put_stone((8,10))
    A.put_stone((8,11))
    print(str(A))