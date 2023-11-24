
# test
import kaxe

class Test:

    def normalWithoutObjects():
        plot = kaxe.Plot()

        plot.save('normalWithoutObjects.png')


    def diagonalAxisWithoutObjects():
        plot = kaxe.Plot()

        first = kaxe.Axis()
        second = kaxe.Axis()

        plot.setFirstAxis(first)
        plot.setSecondAxis(second)

        plot.save('diagonalAxisWithoutObjects.png')


if __name__ == '__main__':
    Test.normalWithoutObjects()
    Test.diagonalAxisWithoutObjects()
