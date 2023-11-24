
# test
import kaxe

class Test:

    def normal():
        plot = kaxe.Plot()

        plot.save('normal.png')


    def pointPlot():
        plot = kaxe.Plot()

        p = kaxe.objects.Points(range(0,100), [0.25*i**2 for i in range(0,100)])
        plot.add(p)

        plot.save('pointPlot.png')

    
    def labels():
        plot = kaxe.Plot()
        plot.title('hej', 'en lang titel der strækker sig langt')

        p = kaxe.objects.Points(range(0,100), [0.25*i**2 for i in range(0,100)])
        plot.add(p)

        plot.save('labels.png')


    def customAxis():
        
        plot = kaxe.Plot()
        plot.title('hej', 'en lang titel der strækker sig langt')

        # p = kaxe.objects.Points(range(0,100), [0.25*i**2 for i in range(0,100)])
        p = kaxe.objects.Points(range(0,100), range(0,200,2))
        plot.add(p)

        first = kaxe.Axis((2,1))
        second = kaxe.Axis((1,0))

        plot.setAxis(first, second)

        plot.save('customaxis.png')
    

    def skewedTrueAxis():
        
        plot = kaxe.Plot(trueAxis=True)
        plot.title('hej', 'en lang titel der strækker sig langt')

        # p = kaxe.objects.Points(range(0,100), [0.25*i**2 for i in range(0,100)])
        p = kaxe.objects.Points(range(10000,100000), range(10000,100000))
        plot.add(p)

        first = kaxe.Axis((2,1))
        second = kaxe.Axis((1,0))

        plot.setAxis(first, second)

        plot.save('customaxis.png')



if __name__ == '__main__':
    # Test.normalWithoutObjects()
    # Test.diagonalAxisWithoutObjects()
    #Test.customAxis()
    # Test.normal()
    Test.customAxis()
    #Test.labels()



# goals
# fix markers så de er lidt mere konsistente
# lave legendbox til egen klasse