
import sys
sys.path.append('./src')

# test
import math
import kaxe
import unittest

#class TestMethods(unittest.TestCase):
class Test:

    def testNormal():
        plot = kaxe.Plot()

        plot.save('tests/images/normal.png')

    def testPointPlot():
        plot = kaxe.Plot()

        plot.title('en lang titel der strakker sig langt', 'en lang titel der strakker sig langt')

        p = kaxe.objects.Points(range(0,100), [0.25*i**2-100 for i in range(0,100)]).legend('test')
        plot.add(p)

        plot.save('tests/images/pointPlot.png')


    def testLinearPointPlot():
        plot = kaxe.Plot()

        plot.title('en lang titel der strakker sig langt', 'en lang titel der strakker sig langt')

        p = kaxe.objects.Points(range(0,100), [i for i in range(0,100)]).legend('test')
        plot.add(p)

        plot.save('tests/images/pointPlot.png')


    def testLabels():
        plot = kaxe.Plot()
        plot.title('$f(x)=\\cases{2}{x<2}{4*x+2}{x>2}$', 'en lang titel der strækker sig langt')

        p = kaxe.objects.Points(range(0,100), [0.25*i**2 for i in range(0,100)])
        plot.add(p)

        plot.save('tests/images/labels.png')


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

        plot.save('tests/images/customaxis.png')
    


    def testFunction():
        plot = kaxe.Plot()
        
        f1 = kaxe.objects.Function(lambda x, a: a*x, a=2)
        plot.add(f1)
        f1.fill(-10,10)

        f2 = kaxe.objects.Function(lambda x, a: a*x, a=0, width=10)
        plot.add(f2)

        f3 = kaxe.objects.Function(lambda x: math.sin(x)*2)
        f3.tangent(2)
        f3.fill(-math.pi, math.pi)
        plot.add(f3)

        f4 = kaxe.objects.Function(lambda x: math.sqrt(x))
        plot.add(f4)
        f4.fill(4,8)

        f5 = kaxe.objects.Function(lambda x: 1/x)
        plot.add(f5)
        f5.fill(4,8)

        plot.save('tests/images/function.png')

    
    def testInverseProportional():
        plot = kaxe.Plot()
        
        f5 = kaxe.objects.Function(lambda x: 1/x)
        plot.add(f5)
        f5.fill(4,8)

        plot.save('tests/images/inverseprop.png')


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

        plot.save('tests/images/piecewise.png')



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

        plot.save('tests/images/pillars.png')
    
    
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

        plot.save('tests/images/equation.png')


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

        plot.save('tests/images/colormap.png')

    
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

        plt.save('tests/images/logarithmic.png')


    def testThemes():

        plot = kaxe.Plot([-10, 10, -10, 10])
        
        plot.theme(kaxe.Themes.A4Full)

        eq = kaxe.objects.Equation(lambda x, y: math.sin(y)*4, lambda x,y: x)
        plot.add(eq)

        plot.save('tests/images/theme_full.png')

        plot = kaxe.Plot([-10, 10, -10, 10])
        
        plot.theme(kaxe.Themes.A4Half)

        eq = kaxe.objects.Equation(lambda x, y: math.sin(y)*4, lambda x,y: x)
        plot.add(eq)

        plot.save('tests/images/theme_half.png')
    

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

        plt.title('en titel på radius ting')

        # steps = [(i/1000)*math.pi*2 for i in range(0, 1000)]
        # p = kaxe.objects.Points(steps, [math.sin(i) for i in steps], connect=True).legend('test')
        # plt.add(p)
        
        # p = kaxe.objects.Points(range(0,100), [i/2 for i in range(0,100)], connect=True).legend('test')
        # plt.add(p)

        plt.save('tests/images/polar.png')


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
        basef.legend('f')
        plt.add(basef)

        for N in range(2, 10):
            f = kaxe.Function(s_N, N=N)
            f.legend(f'N={N}')
            plt.add(f)

        f = kaxe.Function(s_N, N=1000)
        f.legend('N=1000')
        plt.add(f)

        plt.save('tests/images/box.png')


    def testStyles():
        plt = kaxe.Plot()

        plt.style({
            "Marker.tickWidth":5,
            "Marker.tickLength":30,
            "Marker.showNumber": True
        })

        plt.style(width=1500, height=1500)

        plt.help()

        plt.save('tests/images/styles.png')

    
    def testLinearFunction():
        plt = kaxe.Plot([-5, 5, -5, 5])

        func = kaxe.Function(lambda x: x)

        plt.add(func)

        plt.save('tests/images/linearfunc.png')


    def testBoxPlotNoGridLines():
        
        #plt = kaxe.Plot([-4, 4, -2, 5])
        plt = kaxe.BoxPlot([-math.pi-1, math.pi+1, -1, 4])

        plt.help()
        plt.style({'marker.showLine':False})

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
        basef.legend('f')
        plt.add(basef)

        for N in range(2, 10):
            f = kaxe.Function(s_N, N=N)
            f.legend(f'N={N}')
            plt.add(f)

        f = kaxe.Function(s_N, N=1000)
        f.legend('N=1000')
        plt.add(f)

        plt.save('tests/images/boxnogridline.png')


    def testPieChart():
        chart = kaxe.chart.Pie()

        chart.add(19, 'n1')
        chart.add(6, 'n2')
        chart.add(8, 'n3')
        chart.add(58, 'n4')
        chart.add(25, 'n4')

        chart.title('$x^2$ er nu en lang lang laaaang titel')

        chart.save('tests/images/piechart.png')
    

    def testBarChart():
        chart = kaxe.chart.Bar()

        chart.add(2013, 2.8)
        chart.add(2014, 3.1)
        chart.add(2015, 3.3)
        chart.add(2016, 3.6)
        chart.add(2017, [4, 1])
        chart.add(2018, 4.3)
        chart.add(2019, 4.6)
        chart.add(2020, 5)
        chart.add(2021, [5.5, 2, 1])
        chart.add(2022, [5.9, 1])
        chart.add(2023, [6.4, 0, 1])

        chart.legends('Profit', 'Marked', 'Andre buzzwords')

        chart.title('$x^2$ er nu en lang lang laaaang titel', '$x^2$ er nu en lang lang laaaang titel', '$x^2$ er nu en lang lang laaaang titel')

        chart.style(rotateLabel=45)

        chart.save('tests/images/barchart.png')

        # rotate
        chart = kaxe.chart.Bar(True)

        chart.add(2013, 2.8)
        chart.add(2014, 3.1)
        chart.add(2015, 3.3)
        chart.add(2016, 3.6)
        chart.add(2017, [4, 1])
        chart.add(2018, 4.3)
        chart.add(2019, 4.6)
        chart.add(2020, 5)
        chart.add(2021, [5.5, 2, 1])
        chart.add(2022, [5.9, 1])
        chart.add(2023, [6.4, 0, 1])

        chart.legends('Profit', 'Marked', 'Andre buzzwords')

        chart.title('$x^2$ er nu en lang lang laaaang titel', '$x^2$ er nu en lang lang laaaang titel', '$x^2$ er nu en lang lang laaaang titel')

        chart.save('tests/images/barchart_rotate.png')


    def testGroupBarChart():
        chart = kaxe.chart.GroupBar()

        chart.add(2013, 2.8)
        chart.add(2014, 3.1)
        chart.add(2015, 3.3)
        chart.add(2016, 3.6)
        chart.add(2017, [4, 1])
        chart.add(2018, 4.3)
        chart.add(2019, 4.6)
        chart.add(2020, 5)
        chart.add(2021, [5.5, 2, 1])
        chart.add(2022, [5.9, 1])
        chart.add(2023, [6.4, None, 1])

        chart.legends('Profit', 'Marked', 'Andre buzzwords')

        chart.title('$x^2$ er nu en lang lang laaaang titel', '$x^2$ er nu en lang lang laaaang titel', '$x^2$ er nu en lang lang laaaang titel')

        chart.style(rotateLabel=0)

        chart.save('tests/images/groupbarchart.png')

        # rotate
        chart = kaxe.chart.GroupBar(True)

        chart.add(2013, 2.8)
        chart.add(2014, 3.1)
        chart.add(2015, 3.3)
        chart.add(2016, 3.6)
        chart.add(2017, [4, 1])
        chart.add(2018, 4.3)
        chart.add(2019, 4.6)
        chart.add(2020, 5)
        chart.add(2021, [5.5, 2, 1])
        chart.add(2022, [5.9, 1])
        chart.add(2023, [6.4, None, 1])

        chart.legends('Profit', 'Marked', 'Andre buzzwords')

        chart.title('$x^2$ er nu en lang lang laaaang titel', '$x^2$ er nu en lang lang laaaang titel', '$x^2$ er nu en lang lang laaaang titel')

        chart.save('tests/images/groupbarchart_rotate.png')


    def testCarsten():
        c1 = kaxe.chart.Bar()

        c1.add(2013, 2.8*6.89)
        c1.add(2014, 3.1*6.89)
        c1.add(2015, 3.3*6.89)
        c1.add(2016, 3.6*6.89)
        c1.add(2017, 4*6.89)
        c1.add(2018, 4.3*6.89)
        c1.add(2019, 4.6*6.89)
        c1.add(2020, 5*6.89)
        c1.add(2021, 5.5*6.89)
        c1.add(2022, 5.9*6.89)
        c1.add(2023, 6.4*6.89)

        c1.title(secondAxis='Markedsværdi i milliarder DKK')

        c1.style(rotateLabel=45, barColor=(111, 196, 119, 255))

        c1.save('tests/images/carsten_1.png')

        # c2
        c2 = kaxe.chart.Bar()

        c2.add(2023, 19460)
        c2.add(2024, 22120)
        c2.add(2025, 23630)
        c2.add(2026, 29380)
        c2.add(2027, 34850)

        c2.title(secondAxis='Forventet antal installerede vindmøller')

        c2.style(rotateLabel=45, barColor=(111, 196, 119, 255))

        c2.save('tests/images/carsten_2.png')

        # c3
        c3 = kaxe.chart.GroupBar(True)

        c3.add("Personbiler", [67163.77, 55834.46, 57054.3, 61598.65])
        c3.add("Lette kommercielle køretøjer", [20512.8, 17206.44, 18593.85, 19860.13])
        c3.add("Tunge kommercielle køretøjer", [4152.41, 4361.42, 4298.78 ,3304.75])
        c3.add("Tunge busser", [346.83, 219.27, 199.06, 253.2])

        c3.legends('2019', '2020', '2021', '2022')

        c3.title(secondAxis="Produktion i tusinde enheder")

        c3.style(barColor=[
            (111, 196, 119, 255),
            (0, 0, 0, 255),
            (208, 220, 208, 255),
            (37, 91, 42, 255)
        ])

        #c3.style(rotateLabel=45, barColor=(111, 196, 119, 255))

        c3.save('tests/images/carsten_3.png')

        # c4
        c4 = kaxe.chart.Pie()

        c4.add(35, "Andre", '35%')
        c4.add(30, "Luftfartsindustrien og forsvaret", '30%')
        c4.add(13, "Bilindustrien", '13%')
        c4.add(22, "Vindenergi", '22%')

        #c3.title(secondAxis='Produktion i tusinde enheder')

        c4.style(pieColor=[
            (111, 196, 119, 255),
            (0, 0, 0, 255),
            (111, 196, 119, 50),
            (37, 91, 42, 255)
        ])

        #c3.style(rotateLabel=45, barColor=(111, 196, 119, 255))

        c4.save('tests/images/carsten_4.png')

        # c5
        c5 = kaxe.chart.Pie()

        c5.add(96.7, "Snor", '96,7s')
        c5.add(14.1, "Ring på aksel", '14.1s')
        c5.add(14.4, "Sok", '14,4s')
        c5.add(31.2, "Afmontering ring", '31,2s')
        c5.add(9.6, "Huggepipe", '9,6s')

        #c3.title(secondAxis='Produktion i tusinde enheder')

        c5.style(pieColor=[
            (111, 196, 119, 255),
            (0, 0, 0, 255),
            (37, 91, 42, 255),
            (111, 196, 119, 125),
            (183,225,187, 255)
        ], phaseshift=60)

        #c3.style(rotateLabel=45, barColor=(111, 196, 119, 255))

        c5.save('tests/images/carsten_5.png')


if __name__ == '__main__':
    if True:
        Test.testBoxPlotNoGridLines()
        Test.testPolarPlot()
        Test.testLabels()
        Test.testFunction()
        Test.testPillars()
        Test.testEquation()
        Test.testColorMap()
        Test.testThemes()
        Test.testInverseProportional()
        Test.testPiecewise()
        Test.testPointPlot()
        Test.testNormal()
        Test.testLogarithmic()
        Test.testLinearFunction()
        Test.testBarChart()
        Test.testPieChart()
        Test.testGroupBarChart()
        Test.testCarsten()
        Test.testBoxPlot()
