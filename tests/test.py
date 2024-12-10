
import sys
sys.path.append('./src')

# test
import math
import kaxe
from random import randint
import numpy as np

class Test:
    def argument():
        if len(sys.argv) == 1:
            Test.run()
        else:
            eval('Test.test{}()'.format(sys.argv[1]))

    def run():
        for i in dir(Test):
            if 'test' in i:
                eval('Test.{}()'.format(i))

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

        plot.title('hejsa')

        p = kaxe.objects.Points(range(0,100), [i for i in range(0,100)]).legend('test')
        plot.add(p)

        plot.save('tests/images/pointPlot.png')
        #plot.show()


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

        plt = kaxe.LogPlot([0, 4121, 0, 1212], firstAxisLog=True, secondAxisLog=True)
        plt.save('tests/images/loglog.png')

    def testPrettyLogarithmic():
        plt = kaxe.LogPlot([0, 4121, 0, 1212])
        plt.add(kaxe.Points([0, 500, 1000, 1500, 2000, 2500], [1, 5, 10, 50, 100, 500, 1000], connect=True))
        plt.save('tests/images/logarithmic2.png')


    def testThemes():

        plot = kaxe.Plot([-10, 10, -10, 10])
        
        plot.theme(kaxe.Themes.A4Large)

        eq = kaxe.objects.Equation(lambda x, y: math.sin(y)*4, lambda x,y: x)
        plot.add(eq)

        plot.save('tests/images/theme_full.png')

        plot = kaxe.Plot([-10, 10, -10, 10])
        
        plot.theme(kaxe.Themes.A4Small)

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


    def testCharts():
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

        c1.style({"axis.stepSizeBand": [400, 200]}, rotateLabel=45, barColor=(111, 196, 119, 255), fontSize=75)
        

        c1.save('tests/images/carsten_1.png')

        # c2
        c2 = kaxe.chart.Bar()

        c2.add(2023, 19460)
        c2.add(2024, 22120)
        c2.add(2025, 23630)
        c2.add(2026, 29380)
        c2.add(2027, 34850)

        c2.title(secondAxis='Forventet antal installerede vindmøller')

        c2.style({"axis.stepSizeBand": [400, 200]}, rotateLabel=45, barColor=(111, 196, 119, 255), fontSize=75)

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

        # c3 b
        c3b = kaxe.chart.Bar(True)

        c3b.add("Personbiler", 61598.65/1000)
        c3b.add("Lette kommercielle køretøjer", 19860.13/1000)
        c3b.add("Tunge kommercielle køretøjer", 3304.75/1000)
        c3b.add("Tunge busser", 253.2/1000)

        c3b.legends('2022')

        c3b.title(secondAxis="Produktion i millioner enheder")

        c3b.style(barColor=(111, 196, 119, 255), fontSize=75)

        #c3.style(rotateLabel=45, barColor=(111, 196, 119, 255))

        c3b.save('tests/images/carsten_3b.png')

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

        c4.style(pieColor=[
            (111, 196, 119, 50),
            (0, 0, 0, 255),
            (111, 196, 119, 50),
            (111, 196, 119, 50)
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
        c5.add(10, "Kvalitetstjek", '10s')

        #c3.title(secondAxis='Produktion i tusinde enheder')

        c5.style(pieColor=[
            (111, 196, 119, 255),
            (0, 0, 0, 255),
            (37, 91, 42, 255),
            (111, 196, 119, 125),
            (100,100,100, 255),
            (200,200,200, 255)
        ], phaseshift=60)

        #c3.style(rotateLabel=45, barColor=(111, 196, 119, 255))

        c5.save('tests/images/carsten_5.png')


        c6 = kaxe.chart.Pie()

        c6.add(47.7, 'Nordamerika', '47700t')
        c6.add(43.9, 'Europa', '43900t')
        c6.add(30.3, 'Asien og Stillehavet', '30300t')
        c6.add(4.8, 'Resten af verden', '4800t')

        c6.style(pieColor=[
            (111, 196, 119, 255),
            (0, 0, 0, 255),
            (37, 91, 42, 255),
            (111, 196, 119, 125),
        ], phaseshift=60, fontSize=70)

        c6.save('tests/images/carsten_6.png')


        # c7
        c7 = kaxe.chart.Bar()

        # c7.add(0.119288889, 'Raytheon Technologies', '11,9%')
        # c7.add(0.1184, 'Boeing', '11,8%')
        # c7.add(0.117333333, 'Lockheed Martin', '11,7%')
        # c7.add(0.1152, 'Airbus Americas', '11,5%')
        # c7.add(0.065066667, 'Northrop Grumman', '6,5%')
        # c7.add(0.047644444, 'GE Aviation', '4,7%')
        # c7.add(0.028266667, 'Rolls-Royce Holdings Plc', '2,8%')
        # c7.add(0.022933333, 'Textron Aviation', '2,2%')
        # c7.add(0.020977778, 'Honeywell Arospace', '2,1%')
        # c7.add(0.0048, 'Leonardo DRS', '0,5')
        # c7.add(0.340088889, 'Andre', '34,0%')

        c7.add("Luftfarts", [65.99*0.3, 34.01*0.3])
        c7.add("Vindmølle", [84.77*0.22, 15.23*0.22])
        c7.add("Bil", [48.6*0.13, 51.4*0.13])
        c7.add("Andre", [0, 35])

        print(65.99*0.3 + 84.77*0.22 + 48.6*0.13)

        c7.style({"axis.stepSizeBand": [400, 200]}, barColor=[
            (111, 196, 119, 255),
            (150, 150, 150, 255),
            # (208-50, 220-50, 208-50, 255),
        ], barGap=125, width=2000, height=1000, fontSize=75, rotateLabel=0)

        c7.title(secondAxis="Markedsandel i procent", firstAxis="Industrier")

        c7.legends('De 10 største virksomheder', 'Andre')

        c7.save('tests/images/carsten_7.png')

        # c8
        c8 = kaxe.chart.Pie()

        a = 65.99*0.3 + 84.77*0.22 + 48.6*0.13
        c8.add(a, 'Potientielle kunder', f'{round(a, 2)}%')
        c8.add(100-a, 'Andre', f'{100-round(a, 2)}%')

        c8.style(pieColor=[
            (111, 196, 119, 255),
            (150, 150, 150, 255),
            #(208-50, 220-50, 208-50, 255)
        ],phaseshift=99.5, fontSize=75, width=1500)

        c8.save('tests/images/carsten_8.png')

    def testEmptyPlot():
        if True:
            plt = kaxe.EmptyPlot([-2, 2, -2, 2])
            func = kaxe.Function(lambda x: 2*x**3 - 2 * x)
            plt.add(func)
            plt.save('tests/images/emptyplot.png')

        if True:
            plt = kaxe.EmptyPlot([0, 2, 0, 2])
            func = kaxe.Function(lambda x: x)
            plt.add(func)
            plt.save('tests/images/emptyplot2.png')
        
    def testEmptyWindow():
        plt = kaxe.EmptyWindow([0, 10, 0, 10])
        func = kaxe.Function(lambda x: 2*(x-5)**3 - 2 * (x-5) + 5)
        plt.add(func)
        plt.save('tests/images/emptywindow.png')
    

    def testParametricEquation():
        plt = kaxe.Plot([-2, 2, -2, 2])
        #func = kaxe.ParametricEquation(lambda t: (math.cos(t), math.sin(t)), [-math.pi,math.pi])
        #func = kaxe.ParametricEquation(lambda t: (math.cos(t), math.sin(t*6)), [-100, 100])
        func = kaxe.ParametricEquation(lambda t: (math.cos(t), math.sin(t)), [0, math.pi])
        plt.add(func)
        plt.save('tests/images/parametricequation.png')

    def testArrow():
        plt = kaxe.Plot([-2, 2, -2, 2])
        arrow = kaxe.Arrow((0,0), (1,1))
        plt.add(arrow)
        arrow = kaxe.Arrow((1,1), (2,-1))
        plt.add(arrow)
        plt.save('tests/images/arrow.png')

    
    def testRootLocus():
        plt = kaxe.Plot([-5, 5, -5, 5])
        
        # (s^5 - 1)/(s^2 + 1)
        #plt.add(kaxe.RootLocus([3, 0, 0, -1], [0, 0, 1, 0], [-5, 5]))
        plt.add(kaxe.RootLocus([1, 0, 0, 0, 0, -1], [0, 0, 0, 1, 0, 1]))
        #plt.add(kaxe.RootLocus([2,5,1], [1,2, 3], [-5, 5]))
        #plt.add(kaxe.RootLocus([2, 5, 1],[1, 2, 3], [0, 10**9]))

        plt.save('tests/images/rootlocus.png')
        #plt.show()


    def test3DAnimation():

        for i in range(0,360, 30):
            plt = kaxe.Plot3D(window=[0,1,0,1,0,1], rotation=[-10,i])
            plt.title('x aksen', 'y aksen', 'z aksen')
            plt.style(width=1000, height=1000, outerPadding=(0,0,0,0))
            
            points = []
            n = 50
            for x in range(1,n):
                x = x / n
                for y in range(1,n):
                    y = y / n
                    points.append((x, y, 2*x*y/(1+x**2)))

            cloud = kaxe.Points3D(
                [x for x,y,z in points],
                [y for x,y,z in points],
                [z for x,y,z in points],
            )#.legend('Kaxe nu i 3D')

            plt.add(cloud)

            plt.save('tests/images/3d/3d-cloud-{}.png'.format(i))
            # ffmpeg -framerate 30 -i tests/images/3d/3d-cloud-%d.png -c:v libx264 -r 30 tests/3d.mp4

    
    def test3DAnimationSingleFrame():
        i = 120

        plt = kaxe.Plot3D(window=[0,1,0,1,0,1], rotation=[-10,i])
        plt.title('x aksen', 'y aksen', 'z aksen')
        plt.style(width=1000, height=1000, outerPadding=(0,0,0,0))
            
        points = []
        n = 50
        for x in range(1,n):
            x = x / n
            for y in range(1,n):
                y = y / n
                points.append((x, y, 2*x*y/(1+x**2)))

        cloud = kaxe.Points3D(
            [x for x,y,z in points],
            [y for x,y,z in points],
            [z for x,y,z in points],
        )#.legend('Kaxe nu i 3D')

        plt.add(cloud)

        plt.save('tests/images/3d/3d-cloud-{}.png'.format(i))


    def test3D():
        
        plt = kaxe.Plot3D(window=[-1,1,-1,1,-0.5,0.5], rotation=[60+45, -20])
        plt.style(width=1000, height=1000)
        plt.help()
        cmap = kaxe.Colormaps.standard
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3, color=cmap, numPoints=500))
        plt.save('tests/images/3d-box.png')

        plt = kaxe.Plot3D(window=[-1,1,-1,1,-0.5,0.5], rotation=[60+45, -20])
        plt.style(width=1000, height=1000, backgroundColor=(0,0,100,255), color=(255,255,255,255))
        cmap = kaxe.Colormaps.green
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3, color=cmap))
        plt.save('tests/images/3d-box-style.png')

        plt = kaxe.PlotFrame3D(window=[-1,1,-1,1,-0.5,0.5], rotation=[60+45, -20])
        plt.style(width=1000, height=1000)
        cmap = kaxe.Colormaps.cream
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3, color=cmap))
        plt.save('tests/images/3d-frame.png')

        plt = kaxe.PlotCenter3D(window=[-1,1,-1,1,0,1], rotation=[60+45, -20])
        plt.style(width=1000, height=1000)
        cmap = kaxe.Colormaps.brown
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3 + 0.5, color=cmap, fill=False))
        plt.save('tests/images/3d-center.png')
        
        plt = kaxe.PlotEmpty3D(window=[-1,1,-1,1,0,1], rotation=[60+45, -20])
        plt.style(width=1000, height=1000, backgroundColor=(0,0,0,0))
        cmap = kaxe.Colormaps.red
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3 + 0.5, color=cmap, fill=False))
        plt.save('tests/images/3d-empty.png')


    def test3Dfunction():
        # virkelig flot
        plt = kaxe.Plot3D()
        plt.add(kaxe.Function(lambda x, y: (x**2+y**2)/10-10))
        plt.save('tests/images/3d-function-pretty.png')

        plt = kaxe.Plot3D()
        plt.add(kaxe.Function(lambda x, y: (x**2+y**2)/10-5))
        plt.save('tests/images/3d-function-cutoff.png')

        def func(x, y):
            
            if (-2 < x < 2) and (-2 < y < 20):
                return x**5/y
            return None

        plt = kaxe.Plot3D()
        plt.add(kaxe.Function(func))
        plt.save('tests/images/3d-function-ugly.png')


    def test3DPretty():
        
        def f(x, b):
    
            return sum([
                math.pow(0.55, n)*math.cos(math.pow(b, n)*math.pi*x) for n in range(0, 50)
            ])

        plt = kaxe.PlotFrame3D([-5, 5, 1, 10, -5, 5])
        plt.title('x', 'b', 'z')
        plt.add(kaxe.Function(f))
        plt.save('tests/images/3d-function-pretty-2.png')

        plt = kaxe.Plot3D()
        plt.add(kaxe.Function(lambda x, y: math.sin(x*y/10)))
        plt.add(kaxe.Function(lambda x, y: math.sin(x*y/10)+5, fill=False))
        plt.add(kaxe.Function(lambda x, y: math.sin(x*y/10)-5, fill=False))
        plt.save('tests/images/3d-function-pretty-3.png')


    def testCrossOverMarker():
        plt = kaxe.BoxPlot([-2000,6000,-1,1])
        plt.save('tests/images/crossover.png')

        plt = kaxe.Plot3D()
        plt.style(width=1000, height=1000)
        plt.help()
        cmap = kaxe.Colormaps.standard
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3, color=cmap))
        plt.save('tests/images/3d-box-2.png')
        plt.show()

    
    def testDottedLine():
        plt = kaxe.Plot()
        
        plt.add(kaxe.Function2D(lambda x: x**2-5, dashed=30))

        plt.save('tests/images/dottedline.png')
        #plt.show()


    def testAllLegends():
        plt = kaxe.Plot()
        plt.add(kaxe.Arrow((0,0), (1,1)).legend('Arrow'))
        plt.add(kaxe.Equation(lambda x,y: x, lambda x,y: 2*y).legend('Equation'))
        plt.add(kaxe.Function2D(lambda x: x**2-4).legend('Funktion'))
        plt.add(kaxe.ParametricEquation(lambda t: (math.sin(t), (t/3)**2), (0, 2*math.pi)).legend('ParametricEquation'))
        plt.add(kaxe.Pillars([0,1,2], [1,2,3], color=(0,0,0,100)).legend('Pillars'))
        plt.add(kaxe.Points([0,1,2,3], [0,1,2,3]).legend('Points'))
        plt.save('tests/images/alllegeneds.png')

        # burde også test3 3d

    def testLollipop():
        start = -2*math.pi
        end = 2*math.pi
        
        plt = kaxe.Plot([start, end, -1.5, 1.5])
        
        func = lambda x: math.sin(x)

        x = []
        y = []
        numPoints = 50
        for i in range(0, numPoints):
            j = (end - start) * i/numPoints + start    
            x.append(j)
            y.append(func(j))

        plt.add(kaxe.Function(func))
        plt.add(kaxe.Points2D(x, y, lollipop=True).legend('Sampling'))

        plt.show()


    def testPointsOutsideAndMultipleLegends():
        
        plt = kaxe.Plot([10, 10.5, None, None])
        plt.style(fontSize=128, outerPadding=(900,500,500,500))
        t = [i/100 for i in range(0,10000)]
        plt.add(kaxe.Points2D(t, [x**2 for x in t], connect=True).legend('$\\frac{a}{b}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('howdi'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\eta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\phi$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\pi$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.LOLLIPOP).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.LOLLIPOP).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.LINE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.LINE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.save('tests/images/testPointsOutsideAndMultipleLegends.png')
        plt.show()

    def testQualityOfLife():
        
        plt = kaxe.Plot([0, 5])
        plt.add(kaxe.Points2D([0,1,2,3], [0,1,2,3]).legend('A'))
        plt.save('tests/images/dump.png')

        plt = kaxe.Plot([0, 5])
        plt.add(kaxe.Points2D([0,1,2,3], [0,0,0,0]))
        plt.save('tests/images/dump.png')

        plt = kaxe.Plot()
        plt.add(kaxe.Function(lambda x: math.sqrt(x)))
        plt.save('tests/images/dump.png')
        # plt.show()

        plt = kaxe.Plot()
        plt.add(kaxe.Points(['hej', 'wow', 'nan', 1, 2], ['a', 'b', 'c', 2, complex(2, 1)]))
        plt.save('tests/images/dump.png')
        # plt.show()


    def testLegendBoxAgain():
        
        plt = kaxe.BoxPlot()
        plt.style(outerPadding=(0,0,0,0))
        plt.add(kaxe.Points([0,1,2], [0,1,2]).legend('Experiment 1'))
        plt.add(kaxe.Points([0,1,2], [0,1,2]).legend('$\\theta=\\theta_0 * \\mu * \\text{e}^{-\\frac{c}{2 *J} * t} * \\cos(\\frac{a * t}{2 * J} + \\alpha)$'))
        plt.add(kaxe.Points([0,1,2], [0,1,2]).legend('Experiment 2'))
        plt.add(kaxe.Points([0,1,2], [0,1,2]).legend('a'))
        plt.add(kaxe.Points([0,1,2], [0,1,2]).legend('Experiment 3'))
        plt.add(kaxe.Points([0,1,2], [0,1,2]).legend('Experiment 4'))
        plt.add(kaxe.Points([0,1,2], [0,1,2]).legend('$\\frac{a}{b}$'))
        plt.add(kaxe.Points([0,1,2], [0,1,2]).legend('$\\theta=\\theta_0 * \\mu * \\text{e}^{-\\frac{c}{2 *J} * t} * \\cos(\\frac{a * t}{2 * J} + \\alpha)$'))
        plt.add(kaxe.Points([0,1,2], [0,1,2]).legend('$\\theta=\\theta_0 * \\mu * \\text{e}^{-\\frac{c}{2 *J} * t} * \\cos(\\frac{a * t}{2 * J} + \\alpha)$'))
        plt.help()
        plt.show()

if __name__ == '__main__':
    
    Test.argument()
