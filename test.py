
# test
import math
import kaxe
import unittest

#class TestMethods(unittest.TestCase):
class Test:

    def testNormal():
        plot = kaxe.Plot()

        plot.save('test/normal.png')

    def testPointPlot():
        plot = kaxe.Plot()

        plot.title('en lang titel der strakker sig langt', 'en lang titel der strakker sig langt')

        p = kaxe.objects.Points(range(0,100), [0.25*i**2-100 for i in range(0,100)]).legend('test')
        plot.add(p)

        plot.save('test/pointPlot.png')


    def testLinearPointPlot():
        plot = kaxe.Plot()

        plot.title('en lang titel der strakker sig langt', 'en lang titel der strakker sig langt')

        p = kaxe.objects.Points(range(0,100), [i for i in range(0,100)]).legend('test')
        plot.add(p)

        plot.save('test/pointPlot.png')


    def testLabels():
        plot = kaxe.Plot()
        plot.title('$f(x)=\\cases{2}{x<2}{4*x+2}{x>2}$', 'en lang titel der strækker sig langt')

        p = kaxe.objects.Points(range(0,100), [0.25*i**2 for i in range(0,100)])
        plot.add(p)

        plot.save('test/labels.png')


    def testCustomAxis():
        return
        
        plot = kaxe.AxisPlot()
        plot.title('hej', 'en lang titel der strækker sig langt')

        # p = kaxe.objects.Points(range(0,100), [0.25*i**2 for i in range(0,100)])
        p = kaxe.objects.Points(range(0,100), range(0,200,2))
        plot.add(p)

        first = kaxe.VectorAxis((2,1))
        second = kaxe.VectorAxis((1,0))

        plot.setAxis(first, second)

        plot.save('test/customaxis.png')
    


    def testFunction():
        plot = kaxe.Plot()
        
        f1 = kaxe.objects.Function(lambda x, a: a*x, a=2)
        plot.add(f1)
        f1.fill(-10,10)

        f2 = kaxe.objects.Function(lambda x, a: a*x, a=0, width=10)
        plot.add(f2)

        f3 = kaxe.objects.Function(lambda x: math.sin(x)*2, width=2)
        f3.tangent(2)
        f3.fill(-math.pi, math.pi)
        plot.add(f3)

        f4 = kaxe.objects.Function(lambda x: math.sqrt(x))
        plot.add(f4)
        f4.fill(4,8)

        f5 = kaxe.objects.Function(lambda x: 1/x)
        plot.add(f5)
        f5.fill(4,8)

        plot.save('test/function.png')

    
    def testInverseProportional():
        plot = kaxe.Plot()
        
        f5 = kaxe.objects.Function(lambda x: 1/x)
        plot.add(f5)
        f5.fill(4,8)

        plot.save('test/inverseprop.png')


    def testPiecewise():
        plot = kaxe.Plot()
        
        def f(x):
            
            if x < -1:
                return 2

            elif x > 2:
                return x*2-4
            else:
                return -x*2+4

        f5 = kaxe.objects.Function(f)
        plot.add(f5)

        plot.save('test/piecewise.png')



    def testPillars():
        #gaussian distribution

        plot = kaxe.Plot([-40, 30, None, None])
        
        sigma = 10
        mu = 0
        f = lambda x: (1/(sigma*math.sqrt(2*math.pi))*math.e**(-1/2*(((x-mu)/sigma)**2)))

        # x = range(-40,40)
        x = range(0,40)

        pillars = kaxe.objects.Pillars(x, [f(i) for i in x])
        plot.add(pillars)

        func = kaxe.objects.Function(f)
        plot.add(func)

        plot.save('test/pillars.png')
    
    
    def testEquation():

        plot = kaxe.Plot([-10, 10, -10, 10])
        
        center = (0,1)
        eq1 = kaxe.objects.Equation(lambda x, y: (x-center[0])**2+(y-center[1])**2, lambda x,y: 2**2)
        plot.add(eq1)

        eq2 = kaxe.objects.Equation(lambda x, y: (x-center[0])**2+(y-center[1])**2, lambda x,y: 6**2)
        plot.add(eq2)

        eq3 = kaxe.objects.Equation(lambda x, y: math.sin(8*x), lambda x,y: y)
        plot.add(eq3)

        eq4 = kaxe.objects.Equation(lambda x, y: 4*x, lambda x,y: y)
        plot.add(eq4)

        eq5 = kaxe.objects.Equation(lambda x, y: math.sin(y)*4, lambda x,y: x)
        plot.add(eq5)

        plot.save('test/equation.png')


    def testColorMap():
        #gaussian distribution

        plot = kaxe.Plot()
                
        size = (1000, 1000)

        sigma = size[0]/2
        mu = 0
        f = lambda x: (1/(sigma*math.sqrt(2*math.pi))*math.e**(-1/2*(((x-mu)/sigma)**2)))*100
        f = lambda x,y: math.sin(x/100)*100*math.e**(y/1000)

        #data = [[f(math.sqrt(math.pow(x-size[0]//2,2)+math.pow(y-size[1]//2,2))) for x in range(size[0])] for y in range(size[1])]
        data = [[f(x,y) for x in range(size[0])] for y in range(size[1])]

        cmap1 = kaxe.objects.ColorMap(data)
        plot.add(cmap1)

        plot.save('test/colormap.png')

    
    def testLogarithmic():
        
        plt = kaxe.LogPlot([0, 100, 0.01, 10000000000])

        p = kaxe.objects.Points(range(0,100), [i*1000 for i in range(0,100)])
        f1 = kaxe.objects.Function(lambda x: 10*x)
        f2 = kaxe.objects.Function(lambda x: math.pow(10, x))
        plt.add(p)
        plt.add(f1)
        plt.add(f2)

        p1 = kaxe.objects.Points([10, 20, 30, 40, 50, 60], [0.1, 0.05, 0.075, 0.1, 1, 0.015])
        plt.add(p1)

        plt.save('test/logarithmic.png')


    def testThemes():

        plot = kaxe.Plot([-10, 10, -10, 10])
        
        plot.theme(kaxe.Themes.A4Full)

        eq = kaxe.objects.Equation(lambda x, y: math.sin(y)*4, lambda x,y: x)
        plot.add(eq)

        plot.save('test/theme_full.png')

        plot = kaxe.Plot([-10, 10, -10, 10])
        
        plot.theme(kaxe.Themes.A4Half)

        eq = kaxe.objects.Equation(lambda x, y: math.sin(y)*4, lambda x,y: x)
        plot.add(eq)

        plot.save('test/theme_half.png')
    

    def testPolarPlot():
        
        plt = kaxe.PolarPlot([0,7])

        f = kaxe.objects.Function(lambda x: math.sin(x)*math.cos(x))
        plt.add(f)

        f = kaxe.objects.Function(lambda x: 0.5)
        plt.add(f)

        f = kaxe.objects.Function(lambda x: x)
        plt.add(f)

        eq = kaxe.objects.Equation(lambda x,y: y, lambda x,y: 3)
        plt.add(eq)

        eq = kaxe.objects.Equation(lambda x,y: y, lambda x,y: x)
        plt.add(eq)

        steps = [(i/1000)*math.pi*2 for i in range(0, 1000)]
        p = kaxe.objects.Points(steps, [math.cos(i) for i in steps], connect=True).legend('test')
        plt.add(p)

        # steps = [(i/1000)*math.pi*2 for i in range(0, 1000)]
        # p = kaxe.objects.Points(steps, [math.sin(i) for i in steps], connect=True).legend('test')
        # plt.add(p)
        
        # p = kaxe.objects.Points(range(0,100), [i/2 for i in range(0,100)], connect=True).legend('test')
        # plt.add(p)

        plt.save('test/polar.png')


    def testBoxPlot():
        
        #plt = kaxe.Plot([-4, 4, -2, 5])
        plt = kaxe.BoxPlot([-math.pi-1, math.pi+1, -1, 4])

        def s_N(x, N):
            if -math.pi < x < math.pi:
                return math.pi / 4 + sum([
                    ((1 - (-1)**n)/(n**2 * math.pi)) * (math.cos(n * x)) + 1/n * math.sin(n * x) for n in range(1, N)
                ])
            return math.nan

        def base(x):
            if -math.pi < x < 0:
                return 0
            elif 0 <= x < math.pi:
                return math.pi - x

            return math.nan

        basef = kaxe.Function(base)
        plt.add(basef)

        for N in range(2, 10):
            f = kaxe.Function(s_N, N=N)
            plt.add(f)

        f = kaxe.Function(s_N, N=1000)
        plt.add(f)

        plt.save('test/box.png')


    def testStyles():
        plt = kaxe.Plot()

        plt.style({
            "Marker.tickWidth":5,
            "Marker.tickLength":30,
            "Marker.showNumber": True
        })

        plt.style(width=1500, height=1500)

        plt.help()

        plt.save('test/styles.png')


if __name__ == '__main__':
    if True:
        Test.testPolarPlot()
        Test.testLabels()
        Test.testFunction()
        Test.testPillars()
        Test.testEquation()
        Test.testColorMap()
        Test.testThemes()
        Test.testInverseProportional()
        Test.testPiecewise()
        Test.testEquation()
        Test.testPointPlot()
        Test.testNormal()
        Test.testLogarithmic()
        Test.testBoxPlot()
