
import sys
sys.path.append('./src')

# test
import math
import kaxe
from random import randint
import numpy as np
import random, string
import scipy.interpolate
import time


def randomObject():
    
    pointLength = randint(50, 1000)

    a = randint(-1000000,1000000)
    b = randint(-1000000,1000000)

    l = min(a, b)
    u = max(a, b)

    x = [randint(l, u) for i in range(pointLength)]
    y = [randint(l, u) for i in range(pointLength)]

    point = kaxe.Points2D(x, y)
    
    point.legend(str(a))
    
    return point
    

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


class Test:
    def argument():
        if len(sys.argv) == 1:
            Test.run()
        else:
            eval('Test.test{}()'.format(sys.argv[1]))

    def run():
        for i in dir(Test):
            if 'test' in i:
                print('\033[94m' + 'Running {}'.format(i) + '\033[0m')
                try:
                    now = time.time()
                    eval('Test.{}()'.format(i))
                    print('\033[92m'+ 'Ran {} successfull in {} ms'.format(i, 1000*(time.time() - now)))
                except Exception:
                    print('\033[91m' + 'Error in test {}'.format(i) + '\033[0m')

    def testNormal():
        plot = kaxe.Plot()
        plot.help()

        plot.save('tests/images/normal.png')
        plot.show()

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
        size = (10, 10)
        size = (500, 100)

        sigma = size[0]/2
        mu = 0
        f = lambda x: (1/(sigma*math.sqrt(2*math.pi))*math.e**(-1/2*(((x-mu)/sigma)**2)))*100
        f = lambda x,y: math.sin(x*y/200)*math.e**(y/100)

        #data = [[f(math.sqrt(math.pow(x-size[0]//2,2)+math.pow(y-size[1]//2,2))) for x in range(size[0])] for y in range(size[1])]
        data = [[f(x,y) for x in range(size[0])] for y in range(size[1])]

        cmap1 = kaxe.objects.HeatMap(data)
        cmap1.addColorScale(plot)
        plot.add(cmap1)

        plot.save('tests/images/colormap.png')
        plot.show()

    
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

        for i, theme in enumerate([kaxe.Themes.A4Large, kaxe.Themes.A4Medium, kaxe.Themes.A4Mini, kaxe.Themes.A4Slim, kaxe.Themes.A4Small]):
            plot = kaxe.Plot([-randint(1,100), randint(1,100), -randint(1,100), randint(1,100)])
            plot.theme(theme)
            eq = kaxe.objects.Equation(lambda x, y: math.sin(y)*4, lambda x,y: x)
            plot.add(eq)
            plot.save(f'tests/images/theme_{i}.png')
    

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


    def testBoxedPlot():
        
        #plt = kaxe.Plot([-4, 4, -2, 5])
        plt = kaxe.BoxedPlot([-math.pi-1, math.pi+1, -1, 4])

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

        plt.save('tests/images/boxed.png')


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


    def testBoxedPlotNoGridLines():
        
        #plt = kaxe.Plot([-4, 4, -2, 5])
        plt = kaxe.BoxedPlot([-math.pi-1, math.pi+1, -1, 4])

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
        peq = kaxe.ParametricEquation(lambda t: (math.cos(t), math.sin(t)), [0, math.pi])
        plt.add(peq)
        plt.save('tests/images/parametricequation.png')

        b = 4*math.pi
        plt = kaxe.Plot3D([-2, 2, -2, 2, 0, b])
        omega = 4
        peq = kaxe.ParametricEquation(lambda t: (math.cos(omega*t), math.sin(omega*t), t), [0, b], width=10, color=kaxe.Colormaps.standard)
        plt.add(peq)
        plt.save('tests/images/parametricequation3d.png')
        plt.show()

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


    def __createPoint3DPlot__(rotation):
        plt = kaxe.Plot3D(rotation=rotation, drawBackground=True)
        plt.title('x aksen', 'y aksen', 'z aksen')
        plt.style(width=500, height=500, outerPadding=(0,0,0,0))

        f = plt.add(kaxe.Function3D(lambda x,y: math.sin(x)**2 + y**2 - 9))

        if randint(0,1):
            f.legend('Kaxe nu i 3D')

        plt.save('tests/images/3d/3d-cloud-{}-{}.png'.format(*rotation))


    def test3DRandomFrames():
        
        for _ in range(20):
            Test.__createPoint3DPlot__([randint(-360,360),randint(-360,360)])

    
    def test3DAnimationSingleFrame():
        Test.__createPoint3DPlot__([randint(-360,360),randint(-360,360)])

    def test3D():
        
        plt = kaxe.Plot3D(window=[-1,1,-1,1,-0.5,0.5])
        plt.style(width=1000, height=1000)
        plt.help()
        cmap = kaxe.Colormaps.standard
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3, color=cmap, numPoints=500))
        plt.save('tests/images/3d-box.png')

        plt = kaxe.PlotFrame3D(window=[-1,1,-1,1,-0.5,0.5])
        plt.style(width=1000, height=1000)
        plt.help()
        cmap = kaxe.Colormaps.standard
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3, color=cmap, numPoints=500))
        plt.save('tests/images/3d-frame-2.png')

        plt = kaxe.Plot3D(window=[-1,1,-1,1,-0.5,0.5])
        plt.style(width=1000, height=1000, backgroundColor=(0,0,100,255), color=(255,255,255,255))
        cmap = kaxe.Colormaps.green
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3, color=cmap))
        plt.save('tests/images/3d-box-style.png')

        plt = kaxe.PlotFrame3D(window=[-1,1,-1,1,-0.5,0.5])
        plt.style(width=1000, height=1000)
        cmap = kaxe.Colormaps.cream
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3, color=cmap))
        plt.save('tests/images/3d-frame.png')

        plt = kaxe.PlotCenter3D(window=[-1,1,-1,1,0,1])
        plt.style(width=1000, height=1000)
        cmap = kaxe.Colormaps.brown
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3 + 0.5, color=cmap, fill=False))
        plt.save('tests/images/3d-center.png')
        
        plt = kaxe.PlotEmpty3D(window=[-1,1,-1,1,0,1])
        plt.style(width=1000, height=1000, backgroundColor=(0,0,0,0))
        cmap = kaxe.Colormaps.red
        plt.add(kaxe.Function3D(lambda x,y: x*y**3 -y*x**3 + 0.5, color=cmap, fill=False))
        plt.save('tests/images/3d-empty.png')


    def test3Dfunction():
        # virkelig flot
        plt = kaxe.Plot3D()
        plt.add(kaxe.Function(lambda x, y: (x**2+y**2)/10-10)).legend('$f(x,y)=\\frac{x^2+y^2}{10}-10$')
        plt.save('tests/images/3d-function-pretty.png')
        plt.show()

        plt = kaxe.Plot3D()
        plt.add(kaxe.Function(lambda x, y: (x**2+y**2)/10-5))
        plt.save('tests/images/3d-function-cutoff.png')
        plt.show()

        def func(x, y):
            
            if (-2 < x < 2) and (-2 < y < 20):
                return x**5/y
            return None

        plt = kaxe.Plot3D()
        plt.add(kaxe.Function(func))
        plt.save('tests/images/3d-function-ugly.png')
        plt.show()


    def test3DPretty():
        
        def f(x, b):
    
            return sum([
                math.pow(0.55, n)*math.cos(math.pow(b, n)*math.pi*x) for n in range(0, 50)
            ])

        plt = kaxe.PlotFrame3D([-5, 5, 1, 10, -5, 5])
        plt.title('x', 'y', 'z')
        plt.add(kaxe.Function(f))
        plt.save('tests/images/3d-function-pretty-2.png')

        plt = kaxe.Plot3D()
        plt.add(kaxe.Function(lambda x, y: math.sin(x*y/10)))
        plt.add(kaxe.Function(lambda x, y: math.sin(x*y/10)+5, fill=False))
        plt.add(kaxe.Function(lambda x, y: math.sin(x*y/10)-5, fill=False))
        plt.save('tests/images/3d-function-pretty-3.png')


    def testCrossOverMarker():
        plt = kaxe.BoxedPlot([-2000,6000,-1,1])
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
        plt.add(kaxe.Pillars([0,1,2], [1,2,3], colors=(0,0,0,100)).legend('Pillars'))
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
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('howdi'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\eta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\phi$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\pi$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.LOLLIPOP).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.LOLLIPOP).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.LINE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.TRIANGLE).legend('$\\theta$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.LINE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
        plt.add(kaxe.Points2D(t, [x for x in t], connect=True, symbol=kaxe.Symbol.CIRCLE).legend('$\\frac{a^{a^{a^a}}}{b^c}$'))
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
        
        plt = kaxe.BoxedPlot()
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


    def testTooManyNumbers():
        
        plt = kaxe.Plot()
        plt.style(xNumbers=100, yNumbers=200)
        plt.save('tests/images/toomanynumbers100200.png')

        plt = kaxe.Plot()
        plt.style({"marker.tickWidth":30, "marker.gridlineWidth":50}, xNumbers=5, yNumbers=5)
        plt.add(kaxe.Points([5], [2]))
        plt.save('tests/images/toomanynumberdefault.png')

        for i in [1,2,3,4,5]:
            plt = kaxe.Plot()
            plt.style({"axis.ghostMarkers":i} , xNumbers=6, yNumbers=6)
            plt.add(kaxe.Points([5], [2]))
            plt.save('tests/images/ghostpoints_{}.png'.format(i))

            if i == 5:
                plt.show()


        plt = kaxe.LogPlot()
        plt.style({"axis.ghostMarkers":5} , xNumbers=6, yNumbers=6)
        plt.add(kaxe.Points([5], [2]))
        plt.save('tests/images/ghostpoints_loglog.png'.format(i))
        plt.show()


    def testDobuleAxisPlot():

        plt = kaxe.Plot()
        plt.add(kaxe.Function(lambda x: x))
        # plt.show()
        
        plt = kaxe.DoubleAxisPlot([0, 20, 0, 2, 10, 15])
        
        plt.add1(kaxe.Function2D(lambda x: x).legend('left'))
        plt.add2(kaxe.Function2D(lambda x: x).legend('right'))
        plt.add1(kaxe.Points(range(0,20), range(0,20)).legend('left'))
        plt.add2(kaxe.Points(range(0,20), range(0,20)).legend('right'))

        plt.add1(kaxe.Equation(lambda x,y: (x-1)**2+(y-1)**2, lambda x,y: 1).legend('left'))
        plt.add2(kaxe.Equation(lambda x,y: (x-13)**2+(y-13)**2, lambda x,y: 1).legend('right'))

        plt.title('x', 'y left', 'y right')

        plt.save('tests/images/doubleaxis.png')


    def testBodePlotGrid():

        from scipy.signal import TransferFunction, bode
        
        num = [1, 3, 3]
        den = [1, 2, 1, 1]
        tf = TransferFunction(num, den)
        w, mag, phase = bode(tf, n=1000)

        grid = kaxe.Grid()
        grid.style(width=3000, height=800)

        # magnitude
        plt1 = kaxe.BoxedLogPlot(firstAxisLog=True, secondAxisLog=False)
        plt1.title('$\\omega$ [$\\frac{rad}{s}$]', second="[dB]")
        
        plt1.add(kaxe.Points2D(w, mag, connect=True))

        # plot 2
        plt2 = kaxe.BoxedLogPlot(firstAxisLog=True, secondAxisLog=False)
        plt2.add(kaxe.Points2D(w, phase, connect=True, color=(109,69,76,255)))
        plt2.title(second="[rad]")

        grid.addColumn(plt1, plt2)

        grid.show()

    
    def testGridLayout():
        
        grid = kaxe.Grid()
        
        grid.style(width=500, height=500)

        for i in range(5):
            
            row = []

            for j in range(4):
                
                # magnitude
                plt = kaxe.Plot()
                # plt.style(backgroundColor=(255,200,255,255))
                for i in range(randint(0, 4)):
                    plt.add(randomObject())
                row.append(plt)

            grid.addRow(*row)

        grid.show()
        grid.save('tests/images/gridlayoutlarge.png')


    def testBubbles():
        
        plt = kaxe.Plot([-10, 10, -10, 10])

        plt.add(kaxe.Function(lambda x: x))

        for i in range(2):
            v = randint(-10, 10)
            plt.add(kaxe.Bubble(randomword(randint(1, 20)), (randint(-10, 10), randint(-10, 10)), (v,v)))

        plt.show()


    def testCross():

        plt = kaxe.Plot([-8, 8, -4, 4])

        plt.add(kaxe.Points2D([0, -5.2820, -1.9794, 5.1407], [0, 0, 0, 0], size=50).legend('Plant'))
        plt.add(kaxe.Points2D([-7, -5.2820, -1.9794, -7], [3, 0, 0, -3], size=40, symbol=kaxe.Symbol.CROSS).legend('Placed poles'))

        plt.show()


    def testAddMarkers():
        FARVE1 = (15,163,177,255)
        FARVE2 = (51,44,35,255)
        FARVE3 = (179,57,81,255)
        FARVE4 = (209, 122, 34, 255)
        FARVE5 = (64,78,77,255)
        FARVE6 = (240, 200, 200)

        eu = 0.5
        exd = 0.5

        F_kinetic = 2.8

        x = 0.5

        def frik(u, xdot):

            F_stiction = 3.1
            
            if abs(u) > eu:
                if abs(xdot) > exd:
                    u += F_kinetic*np.sign(xdot)
                else:
                    u += F_stiction*np.sign(xdot)

            return u

        def mod(u, xdot):
            
            F_stiction = -0.463 * x + 3.338

            if abs(u) > eu:

                if abs(xdot) > exd:
                    if xdot > exd:
                        u += F_kinetic
                    if xdot < -exd:
                        u -= F_kinetic
                    
                elif abs(u) < F_stiction:
                    u = np.sign(u) * F_stiction
                
                else:
                    u += np.sign(u) * F_stiction
            
            return u

        grid = kaxe.Grid()

        p1 = kaxe.EmptyPlot([0, 10, 0, 10])
        p1.title('u ind', 'U ud')
        
        p1.secondAxis.add('valter', F_kinetic)
        
        p1.add(kaxe.Function2D(lambda u: u, dashed=50, color=FARVE5, width=5).legend('Uden kompensering', color=(200,200,200,255)))
        p1.add(kaxe.Function2D(frik,  xdot = 0.01, color=FARVE2).legend('Original'))
        p1.add(kaxe.Function2D(mod, xdot = 0.01, color=FARVE3).legend('Modificeret'))

        p2 = kaxe.EmptyPlot([0, 10, 0, 10])
        # p2.firstAxis.addMarkerAtPos(3.1, 'Valter')
        p2.firstAxis

        p2.title('u ind', 'U ud')

        # sæt marker på ved kinetic og sårn
        p2.secondAxis.add('valter', F_kinetic)

        p2.add(kaxe.Function2D(lambda u: u, dashed=50, color=FARVE5, width=5).legend('Uden kompensering', color=(200,200,200,255)))
        p2.add(kaxe.Function2D(frik,  xdot = 1, color=FARVE2).legend('Original'))
        p2.add(kaxe.Function2D(mod, xdot = 1, color=FARVE3).legend('Modificeret'))

        p2.add(kaxe.GhostLegend('Valter', (255,0,0,255), kaxe.symbol.CIRCLE))

        grid.addRow(p1, p2)
        # plt.title('')

        grid.show()


    def testBarPolarPlot():
        
        plt = kaxe.PolarPlot(useDegrees=True)
        
        for _ in range(10):
        
            N = randint(1, 10)
            theta = np.linspace(0.0, 2 * np.pi, N)
            radii = 10 * np.random.rand(N)

            pillar = kaxe.Pillars(list(theta), list(radii), width=random.randint(10, 20))

            # pillar = kaxe.Pillars([math.pi], [5], width=random.randint(1, 10))
            
            plt.add(pillar)

        plt.show()


    def test3DBadFunctions():
        
        plt = kaxe.Plot3D()

        plt.add(kaxe.Function3D(lambda x,y: math.sin(x)**2 + y**2 - 12))
        plt.add(kaxe.Function3D(lambda x,y: -2))

        # plt.show()

        plt = kaxe.Plot3D()

        plt.add(kaxe.Function3D(lambda x,y: math.sin(x)**2 + y**2 - 12, fill=False, numPoints=50))
        plt.add(kaxe.Function3D(lambda x,y: -2, fill=False))

        plt.show()

        plt = kaxe.Plot3D()

        plt.add(kaxe.Function3D(lambda x,y: math.sin(x)**2 + y**2 - 12))
        plt.add(kaxe.Function3D(lambda x,y: -2, fill=False))

        plt.show()


    def testBoxPlot():
        
        boxplot = kaxe.BoxPlot()

        l = ['valter', 'kaxe', 'data3', 'data4']
        symbols = [kaxe.symbol.CIRCLE, kaxe.symbol.CROSS, kaxe.symbol.CIRCLE, kaxe.symbol.CROSS]

        for symb in symbols:
            a, b = randint(-1000, 1000), randint(-1000, 1000)
            a, b = min(a,b), max(a,b)
            data = [randint(a, b) for i in range(1000)]

            for _ in range(randint(0, 100)):
                data.append(randint(-1200, 1200))

            boxplot.add(data, symbol=symb)

        boxplot.legends(*l)

        boxplot.show()


    def testContour():

        def f(x,y):
            return 4 * math.sin(x) + 4 * math.cos(y) + x**2 - y

        plt2d = kaxe.Plot()
        plt2d.add( kaxe.Contour(f) )
        
        plt3d = kaxe.Plot3D(window=[-10, 10, -10, 10, -20, 20], rotation=[45+90, -70])
        plt3d.title('x', 'y')
        plt3d.style(fontSize=40)
        plt3d.add( kaxe.Function3D(f, numPoints=500).legend('$f(x,y)=4 \, \sin{(x)} + 4 \, \cos{(x)} + x^2 - y$') )

        grid = kaxe.Grid()
        grid.style(width=2000, height=2000)

        grid.addRow(plt2d, plt3d)

        grid.show()
        grid.save('tests/images/contourgrid.png')


    def testFillObject():
        
        plt = kaxe.Plot([0, 10])
        
        f = lambda x: x**2 - x*8 + 6
        g = lambda x: x-1
        
        plt.add( kaxe.Fill(f, g) )
        
        plt.add( kaxe.Function(f) )
        plt.add( kaxe.Function(g) )

        plt.show()


    def testProjectionFill():
        
        plt = kaxe.BoxedPlot([2000, 2060, 0, 1000000])
        
        plt.style({'axis.ghostMarkers':2})

        def f(x):
            x -= 2000
            return 300*x**2

        amp = 1.15
        def of(x):
            return f(x)*amp
        def uf(x):
            return f(x)/amp

        def kf(x):
            if x < 2025:
                return f(x)

        func = kaxe.Function2D(f, dashed=30, color=kaxe.getRandomColor())
        func.legend('Projection over the next years')

        color = list(func.color)
        color[3] = 100

        plt.add(kaxe.Fill(of, uf, color=tuple(color)))
        plt.add(kaxe.Function2D(kf, color=func.color))
        plt.add(func)

        plt.show()



    def __createFunc(plt, func, slope, color):
        l = [(x, func(x)+randint(-10,10)/10 ) for x in range(100)]
        xs, ys = [x for x, y in l], [y for x, y in l]
        plt.add( kaxe.Points2D(xs, ys, color=color).legend('Hadouken!') )
        
        x0 = 100
        dx = 5
        y0 = func(x0)

        # slope = 1/8

        a = randint(0,100)/200
        b = randint(0,100)/200
        c = randint(0,100)/200
        d = randint(0,100)/200

        def over(x, slope):
            if x > x0:
                return slope*(x-x0+dx)+y0 + a*math.sin(b*x) + b*math.sin(c*x) + c*math.sin(d*x) + d*math.sin(a*x)
        def under(x, slope):
            if x > x0:
                return -slope*(x-x0+dx)+y0 + a*math.sin(b*x) + b*math.sin(c*x) + c*math.sin(d*x) + d*math.sin(a*x)

        plt.add( kaxe.Fill(lambda x: over(x, slope), lambda x: under(x, slope), color=(color[0], color[1], color[2], 100)) )
        def bf(x):
            if x < x0:
                return func(x)
        def af(x):
            if x > x0:
                return func(x)

        plt.add( kaxe.Function2D(bf, color=color) )
        plt.add( kaxe.Function2D(af, dotted=30, width=5, color=color) )


    def testProjectionFillV2():

        plt = kaxe.Plot([0, 200, -20, 40])

        f1 = lambda x: 10*math.exp(-x/50) + 10
        f2 = lambda x: 30*math.exp(-x/10) - 2
        kaxe.getRandomColor()
        kaxe.getRandomColor()
        for func, slope, color in [(f1, 1/6, kaxe.getRandomColor()), (f2, 1/8, kaxe.getRandomColor())]:
            Test.__createFunc(plt, func, slope, color)
        
        plt.show()


    def testFillV3():
        
        plt = kaxe.Plot([0, 10])
        
        f = lambda x: 1/x

        plt.add( kaxe.Fill(f) )

        plt.show()


    def test2DIn3D():
        
        # cigar
        plt = kaxe.Plot3D([-3, 3, -3, 3, 0, 10], rotation=[20, -30])

        func = lambda x,y: x**2 + y**2 + 2

        plt.add(kaxe.Function3D( func ))
        plt.add(kaxe.Contour( func, a=0 ))

        plt2d = kaxe.Plot([-3, 3, -3, 3])
        plt2d.add(kaxe.Equation( func, lambda x,y: 3 ))
        # plt.show()


    def testPrettyContour2DIn3D():
        # contour flot
        
        plt3d = kaxe.Plot3D([-10, 10, -10, 10, 0, 40], rotation=[-45, -60], drawBackground=True)

        def f(x,y):
            return 4 * math.sin(x) + 4 * math.cos(y) + x**2 - y + 20

        plt3d.add( kaxe.Contour(f, a=0, b=40, steps=20) )
        
        plt3d.style(fontSize=40)
        plt3d.add( kaxe.Function3D(f, numPoints=500).legend('$f(x,y)=4 \, \sin{(x)} + 4 \, \cos{(x)} + x^2 - y$') )

        plt3d.show()
        plt3d.save('tests/images/contour3d.png')

    
    def test3DWidthHeightDiffrence():
        
        plt = kaxe.PlotFrame3D([0,1,0,1,0,1])

        plt.theme(kaxe.Themes.A4Large)

        plt.show()
        

    def test3DStretch():
    
        plt = kaxe.PlotFrame3D([-5, 5, -1, 1, -4, 4], rotation=[60+45, -70], size=[4, 1, 3])
        plt.title('x', 'y', 'z')

        def s(t):
            
            xt = (3 + math.cos(math.sqrt(32)*t))*math.cos(t)
            yt = math.sin(math.sqrt(32) * t)
            zt = (3 + math.cos(math.sqrt(32)*t))*math.sin(t)
        
            return xt, yt, zt

        plt.add(kaxe.ParametricEquation(s, [0, 40*math.pi], color=kaxe.Colormaps.blue).legend('asd'))

        plt.show()

        plt = kaxe.PlotFrame3D([-5, 5, -1, 1, -4, 4], rotation=[60+45, -70], size=True, drawBackground=False)
        plt.title('x', 'y', 'z')

        def s(t):
            
            xt = (3 + math.cos(math.sqrt(32)*t))*math.cos(t)
            yt = math.sin(math.sqrt(32) * t)
            zt = (3 + math.cos(math.sqrt(32)*t))*math.sin(t)
        
            return xt, yt, zt

        plt.add(kaxe.ParametricEquation(s, [0, 40*math.pi], color=kaxe.Colormaps.blue))

        plt.show()


    def testOscar28Feb():        

        c = kaxe.GroupBar()
        c.add('hejsa', [1])
        c.title('aaaaa', 'bbbbb')
        c.save('tests/images/oscarbar1.png')

        c = kaxe.Bar()
        c.add('hejsa', [1])
        c.title('aaaaa', 'bbbbb')
        c.save('tests/images/oscarbar2.png')

        c = kaxe.Bar()
        c.add('2022', [1, 5])
        c.add('2023', [1, 2, 3])
        c.add('2024', [4, 1])
        c.title('aaaaa', 'bbbbb')
        c.show()


    def testAdjust():
        """
        plt.theme(.5, 64) til .5 linewidth og 64 fontsize
        """
        
        for i in [0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.75, 0.8, 0.9, 0.99]:
            plt = kaxe.Plot()
            plt.adjust(i)
            plt.save('tests/images/adjust/{}proc.png'.format(int(i*100)))


    def testMesh():
        
        mesh = kaxe.Mesh.open('tests/Eiffel_tower_sample.STL')
        plt = kaxe.PlotFrame3D(mesh.getBoundingBox(), size=True)
        plt.add(mesh)
        plt.show()

        mesh = kaxe.Mesh.open('tests/terrain.stl')
        xs = [i[0] for i in mesh.mesh]
        ys = [i[1] for i in mesh.mesh]
        zs = [i[2] for i in mesh.mesh]

        plt = kaxe.PlotEmpty3D([min(xs), max(xs), min(ys), max(ys), 3, max(zs)], rotation=[-60, -80], size=True)
        
        plt.add(mesh)
        plt.show()


    def testErrorInGroupBarLegendAndTitle():
        ORANGE = (196, 126, 71, 255) #c47e47
        RED = (155, 5, 0, 255) #9b0500
        BLUE = (62, 137, 174, 255) #3e89ae
        DARKGREY = (50, 50, 50, 255) #323232
        GREY = (100, 111, 111, 255) #6e6f6f

        early_revision = [
            ("Infection", 31.3),
            ("Instability", 10.1),
            ("Loosening", 27.4),
            ("Other", 100 - 31.3 - 27.4 - 10.1)
        ]

        late_revision = [
            ("Infection", 29.5),
            ("Instability", 20.3),
            ("Loosening", 22.2),
            ("Other", 100 - 29.5 - 22.2 - 20.3)
        ]

        ##### BARGROUP
        chart = kaxe.GroupBar()
        chart.adjust(.6)
        for i in range(len(late_revision)):
            assert late_revision[i][0] == early_revision[i][0] # tjek om de har samme label
            chart.add(late_revision[i][0], [late_revision[i][1], early_revision[i][1]])
        chart.title('Reason for Revision', 'Procent')
        chart.legends('Late Revision', 'Early Revision')
        chart.style({'legendbox.topMargin': 0}, barColor=[ORANGE, GREY])
        # chart.save('revision_reason.png')
        chart.show()




if __name__ == '__main__':
    import os
    try:
        os.mkdir('tests/images/3d')
    except FileExistsError:
        pass
    try:
        os.mkdir('tests/images/adjust')
    except FileExistsError:
        pass

    Test.testMesh()
    # Test.testErrorInGroupBarLegendAndTitle()
    