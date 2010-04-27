var SvgNS = 'http://www.w3.org/2000/svg';
var XlinkNS = 'http://www.w3.org/1999/xlink';

FrogRace = (function () {    
    var CHOOSECOLOR = 0;
    var WAITING = 1;
    var PREPARING = 2;
    var RACING = 3;
    var AUTISM = 4;
    var FINISHED = 5;
    
    var state = CHOOSECOLOR;
    var finishLine = 95;
    var startTime;
    var finishTime;
    var timeEllapsedInterval = null;
    
    function object(o) {
        function F() {}
        F.prototype = o;
        return new F();
    }

    var width = 0;
    var height = 0;       
    
    function showCountdown(id)
    {
        var element = document.getElementById(id);
        element.setAttribute('visibility', 'visible');
        setTimeout(function () {
            for (var i = 0; i < element.childNodes.length; i++)
            {
                var childNode = element.childNodes[i];
                if (childNode.beginElement)
                    childNode.beginElement();
            }
        }, 500);
    }
    function makeCountdown(n) {        
        setTimeout(function() {
            showCountdown('countdown-3');
            prepareRace();
        }, 0);
        setTimeout(function() {showCountdown('countdown-2');}, 1000);
        setTimeout(function() {showCountdown('countdown-1');}, 2000);
        setTimeout(function() {
            showCountdown('countdown-hop');
            startRace();
        }, 3000);                
    }    
    
    function makeAnimation(document, attributes) {
        var animate = document.createElementNS(SvgNS, 'animate');
        var list = ['attributeName', 'attributeType', 'begin', 'dur', 'fill', 'from', 'to'];
        for (var i = 0; i < list.length; i++)
        {
            var attribute = list[i];
            if (attributes[attribute] != undefined)
                animate.setAttribute(attribute, attributes[attribute]);
        }
        return animate;
    }
    
    function clickPuddle(x, y)
    {
        var circle = document.createElementNS(SvgNS, 'circle');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', '1');
        circle.setAttribute('class', 'clickpuddle');
        circle.setAttribute('stroke', '#ffff33');
        circle.setAttribute('stroke-width', '1');
        circle.setAttribute('fill', 'none');
        circle.setAttribute('opacity', '0');
        var animateR = makeAnimation(document, {
            attributeName: 'r',
            attributeType: 'XML',
            begin: '0s',
            dur: '1s',
            fill: 'freeze',
            to: '15',
            });
        var animateS = makeAnimation(document, {
            attributeName: 'stroke-width',
            attributeType: 'XML',
            begin: '0s',
            dur: '1s',
            fill: 'freeze',
            to: '15',
            });
        var animateO = makeAnimation(document, {
            attributeName: 'opacity',
            attributeType: 'XML',
            begin: '0.1s',
            dur: '1s',
            fill: 'freeze',
            from: '0.8',
            to: '0',
            });
            
        circle.appendChild(animateR);
        circle.appendChild(animateS);
        circle.appendChild(animateO);
        document.documentElement.appendChild(circle);
        animateR.beginElement();
        animateS.beginElement();
        animateO.beginElement();
        setTimeout(function () { document.documentElement.removeChild(circle); }, 3500);                
    }
    
    function setCountdownTransforms(width, height)
    {
        var elements = ['countdown-3', 'countdown-2', 'countdown-1', 'countdown-hop', 'finished'];
        for (var i = 0; i < elements.length; i++)
        {
            var element = document.getElementById(elements[i]);
            element.setAttribute('transform', 'translate(' + (width/2) + ',' + (height/2) + ')');            
        }
    }
    
    function prepareRace()
    {
        var state = getState();
        if (state == WAITING || state == FINISHED)
        {
            changeState(PREPARING);            
        }
    }
    
    function startRace()
    {
        startTime = new Date();
        timeEllapsedInterval = setInterval(updateClock, 50);
        changeState(RACING);
    }
    
    function updateClock()
    {
        setTime(startTime, new Date());
    }
    
    function clearTime()
    {
        var timerSeconds = document.getElementById('timer-seconds');
        var timerThousandths = document.getElementById('timer-thousandths');        
                
        if (timerSeconds != null)
            timerSeconds.firstChild.nodeValue = '0:00';
        if (timerThousandths != null)
            timerThousandths.firstChild.nodeValue = '.00';
    }
    function setTime(startDate, finishDate)
    {
        var timerSeconds = document.getElementById('timer-seconds');
        var timerThousandths = document.getElementById('timer-thousandths');        
        
        var milliseconds = (finishDate - startTime);
        var wholeSeconds = Math.floor(milliseconds / 1000);
        var partialMilliseconds = milliseconds - wholeSeconds * 1000;
        var hundredths = Math.round(partialMilliseconds / 10);
        
        var minutes = Math.floor(wholeSeconds / 60);
        var seconds = wholeSeconds - minutes * 60;
        var secondsStr = seconds.toString();
        if (seconds < 10)
            secondsStr = '0' + secondsStr;
        var hundredthsStr = hundredths.toString();
        if (hundredths < 10)
            hundredthsStr = '0' + hundredthsStr;
        var str = minutes + ':' + secondsStr;
        if (timerSeconds != null)
            timerSeconds.firstChild.nodeValue = str;
        if (timerThousandths != null)
            timerThousandths.firstChild.nodeValue = '.' + hundredthsStr;
    }
    
    function getState()
    {
        return state;
    }
    
    function changeState(n)
    {
        state = n;
    }
    
    function toggleAutism()
    {
        var state = getState();
        if (state == RACING)
            changeState(AUTISM);
//        else if (state == AUTISM)
//            changeState(RACING);        
    }
    
    function revertToWaiting()
    {
        var state = getState();
        if (state != WAITING)
        {
            clearTime();
        }
        changeState(WAITING);
    }
    
    function onKeyPress(evt)
    {
        var state = getState();
        if (evt.keyCode == 114) // r
        {
            revertToWaiting();
        }
        if (evt.keyCode == 115) // s
        {
            revertToWaiting();
            makeCountdown(3);
        }
        if (evt.keyCode == 97) // a
        {
            toggleAutism();
        }
    }
    
    function onClick(evt)
    {
        clickPuddle(evt.x, evt.y);
        moveFrog(evt.x, evt.y);
    }
    
    function finishRace()
    {
        finishTime = new Date();
        clearInterval(timeEllapsedInterval);
        setTime(startTime, finishTime);
        changeState(FINISHED);
        showCountdown('finished');
    }
    
    function setFrogPosition(width, height)
    {
        var frog = document.getElementById('frog');
        frog.setAttribute('x', width/2);
        frog.setAttribute('y', height - 80);
    }
    
    function removeFrogSelector()
    {
        var frogSelector = document.getElementById('frog-selector-fader');
        frogSelector.beginElement();
        //frogSelector.setAttribute('visibility', 'hidden');
    }
    
    function moveFrog(clickX, clickY)
    {
        var state = getState();
        
        if (state == RACING || state == AUTISM)
        {
            var frog = document.getElementById('frog');
            var frogX = parseInt(frog.getAttribute('x'));
            var frogY = parseInt(frog.getAttribute('y'));
            
            if (state == RACING)
            {            
                var distance = Math.sqrt((clickX - frogX) * (clickX - frogX) + (clickY - frogY) * (clickY - frogY));
                
                //var frogMovementDistance = 50*(distance*distance)/((1+distance*distance*distance)*(1+distance*distance*distance));        
                var frogMovementDistance = 200/distance;
                var newFrogX = ((frogX - clickX) / distance) * frogMovementDistance + frogX;
                var newFrogY = ((frogY - clickY) / distance) * frogMovementDistance + frogY;
                frog.setAttribute('x', newFrogX);
                frog.setAttribute('y', newFrogY);
                if (newFrogY <= finishLine)
                    finishRace();
            }
            else if (state == AUTISM)
            {
                var movement = 6;
                var randomX = Math.random() * (movement * 2) - movement;
                var randomY = Math.random() * (movement * 2) - movement;
                
                var doit = Math.random() * 3;
                // 33% change that a click will actually move the frog. Even then, move it randomly.
                if (doit <= 1)
                {
                    var newFrogX = frogX + randomX;
                    var newFrogY = frogY + randomY;                
                    frog.setAttribute('x', newFrogX);
                    frog.setAttribute('y', newFrogY);
                }
            }
        }
    }

    return {
        hey: function() {                    
            makeCountdown(3);  
        },
    
        onLoad: function() {
            width = document.documentElement.width.baseVal.value;
            height = document.documentElement.height.baseVal.value;
            document.documentElement.addEventListener('keypress', onKeyPress, true);
            document.documentElement.addEventListener('mousedown', onClick, true);
            setCountdownTransforms(width, height);
            setFrogPosition(width, height);
        },
        
        chooseFrog: function(evt) {
            var frog = document.getElementById('frog');            
            var fill = evt.srcElement.correspondingUseElement.getAttribute('fill');
            frog.setAttribute('fill', fill);
            frogFader = document.getElementById('frog-fader');
            frogFader.beginElement();
            removeFrogSelector();
            revertToWaiting();
        },
    }        
})();