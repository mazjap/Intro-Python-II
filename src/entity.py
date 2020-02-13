from item import Item, Weapon, PotionType
from location import Location, Direction
import random

class Entity:
    specialChar = ["|", "-", "*", "x", "@", "▲", "▶", "▼", "◀"]

    def __init__(self, isHostile, isMobile, location, level):
        self.isHostile = isHostile
        self.isMobile = isMobile
        self.location = location
        self.previousLocation = location
        self.level = level
        self.health = level * 2 + 5

    def moveTo(self, x = 0, y = 0):
        if self.isMobile:
            self.location.setX(x)
            self.location.setY(y)

    def getX(self):
        return self.location.getX()

    def getY(self):
        return self.location.getY()

    def getPreviousLocation(self):
        return (self.previousLocation.getX()//2 + 1, self.previousLocation.getY())

    def getDamage(self):
        return self.level * 1.5
    
    def setPreviousLocation(self, x, y):
        self.previousLocation = Location(x, y)

    def moveUp(self):
        self.location.addY(-1)
        self.setPreviousLocation(self.getX(), self.getY())

    def moveDown(self):
        self.location.addY(1)
        self.setPreviousLocation(self.getX(), self.getY())

    def moveLeft(self):
        self.location.addX(-1)
        self.setPreviousLocation(self.getX(), self.getY())

    def moveRight(self):
        self.location.addX(1)
        self.setPreviousLocation(self.getX(), self.getY())

    def getHealth(self):
        return self.health

    def giveHealth(self, health):
        if self.health + health > self.level * 2 + 5:
            self.health = self.level * 2 + 5
        else:
            self.health += health

    def removeHealth(self, health):
        self.health -= int(health)
        if health <= 0:
            self.die()

    def die(self):
        print("I died!")

    def move(self, player, map, possibleDirections):
        pass

    def updateEntity(self, map, player):
        directionList = []
        for direction in Direction:
            if self.entityCanMove(direction, map):
                directionList.append(direction)
            
        prevLoc = self.getPreviousLocation()
        self.move(player, map, directionList)
        map[prevLoc[1]][prevLoc[0]] = " "
        map[self.getY()][self.getX()] = "x"

    def entityCanMove(self, direction, map):
        x = self.getX()
        y = self.getY()
        if direction == Direction.UP:
            if self.checkForChar(map[y-1][x]):
                return False
            else:
                return True
        elif direction == Direction.DOWN:
            if self.checkForChar(map[y+1][x]):
                return False
            else:
                return True
        elif direction == Direction.LEFT:
            if self.checkForChar(map[y][x-1]) or self.checkForChar(map[y][x-2]):
                return False
            else:
                return True
        elif direction == Direction.RIGHT:
            if self.checkForChar(map[y][x+1]) or self.checkForChar(map[y][x + 2]):
                return False
            else:
                return True
        return False
    
    def checkForChar(self, char):
        for val in self.specialChar:
            if val == char:
                return True
        return False


from item import Item, Weapon, WeaponType

class Player(Entity):
    def __init__(self, x = 2, y = 33, health = 10, level = 1, xp = 0):
        super(Player, self).__init__(False, True, Location(x, y), level)
        self.health = health
        self.inventory = []
        self.xp = xp
        self.levelxp = []
        for val in range(1, 11):
            self.levelxp.append(2 ** val)
        self.weapon = Weapon()
        self.updateDamage()

    def giveHealth(self, health):
        self.health += int(health)
        if health > 10:
            health = 10

    def giveXp(self, xp):
        self.xp += xp
        if xp >= self.levelxp[0]:
            self.xp -= self.levelxp[0]
            self.level += 1
            self.levelxp.remove(self.levelxp[0])

    def getHealthSymbols(self):
        return "♥ " * self.health

    def getXp(self):
        return self.xp

    def getDamage(self):
        return int(self.damage * self.weapon.damage)

    def updateDamage(self):
        self.damage = int(self.level * self.weapon.damage)

    def die(self):
        self = Player(level = self.level)

    def __str__(self):
        return f"Health: {self.getHealthSymbols()}| {self.weapon} | Damage: {self.getDamage()} | Level: {self.level} | XP: {self.xp}/{self.levelxp[0]}"


class Enemy(Entity):
    def __init__(self, x, y, level, isMobile = True):
        super(Enemy, self).__init__(True, isMobile, Location(x, y), level)

    def move(self, player, map, possibleDirections): # TODO: Check map for barriers, i.e walls, doors, etc
        playerX = player.getX()
        playerY = player.getY()
        selfX = self.getX()
        selfY = self.getY()
        if (playerX == selfX and (playerY == selfY + 1 or playerY == selfY - 1)):
            player.removeHealth(self.getDamage())
        elif (playerY == selfY and (playerX == selfX + 2 or playerX == selfX - 2)):
            player.takeHealth(self.getDamage())

        if (playerX > selfX - 10 and playerX < selfX + 10) and (playerY > selfY - 5 and playerY < selfY + 5):
            self.moveTowardsPlayer(player, possibleDirections)
        else:
            self.randomMove(possibleDirections)

    def moveTowardsPlayer(self, player, possibleDirections):
        xDistance = self.getX() - player.getPreviousLocation()[0]
        yDistance = self.getY() - player.getPreviousLocation()[1]
        total = abs(xDistance) + abs(yDistance)
        xPercent = abs(xDistance) / total
        rand = random.uniform(0, 1)

        print(f"xPercent: {xPercent}, yPercent: {1 - xPercent}, random number generated: {rand}, x distance from player: {abs(xDistance)}, y distance from player: {abs(yDistance)}")

        if (xDistance >= -10 and xDistance <= 10) and (yDistance >= -5 and yDistance <= 5):
            if rand <= xPercent:
                if xDistance > 0 and Direction.LEFT in possibleDirections:
                    self.moveLeft()
                elif Direction.RIGHT in possibleDirections:
                    self.moveRight()
            else:
                if yDistance > 0 and Direction.UP in possibleDirections:
                    self.moveUp()
                elif Direction.DOWN in possibleDirections:
                    self.moveDown()
        else:
            self.randomMove(possibleDirections)

    def randomMove(self, possibleDirections):
        rand = random.randint(0, len(possibleDirections) - 1)
        move = possibleDirections[rand]
        if move == Direction.UP:
            self.moveUp()
        elif move == Direction.DOWN:
            self.moveDown()
        elif move == Direction.LEFT:
            self.moveLeft()
        elif move == Direction.RIGHT:
            self.moveRight()