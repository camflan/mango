/* defaults */
var currTime = 0;
var currTrack = 0;
var isReady = false;
var p;
var playerState = 'IDLE';

function playerReady(obj) 
{
    var id = obj['id'];
    var version = obj['version'];
    var client = obj['client'];
    isReady = true;
    p = $('#openplayer')[0]
    p.addModelListener('STATE','updatePlayerState');
    p.addModelListener('TIME','updateTrackTime');
    p.addControllerListener('ITEM','updateCurrTrack');
}

$(document).ready(function(){ 
    setup_song_events();
    $('.banner').css('background', '{{ tape.banner_color }}');
});

function updatePlayerState(obj)
{
    playerState = obj.newstate;
    if(playerState == 'COMPLETED')
        endOfTrack();
}

function endOfTrack()
{
    clearClocks();
    playlistArray = p.getPlaylist();
    if(currTrack + 1 >= playlistArray.length)
    {
        currTrack = 0;
        p.sendEvent("STOP");
    }
    else
        p.sendEvent("ITEM", currTrack + 1);
}

function updateTrackTime(obj) {$('li#' + currTrack + '.song .clock').text(duration_prettify(obj.position));}
function updateCurrTrack(obj) {currTrack = obj.index;}
function clearClocks() {$('li.song .clock').text('');}

function duration_prettify(seconds)
{
    seconds = Math.round(seconds);
    if(seconds == currTime) return;
    else 
    {
        var s = seconds%60;
        var m = ((seconds - s)/60);
        m = m ? m+':' : '';
        s = m ? (s < 10 ? '0'+s : s) : s;
    }
    currTime = seconds;
    return m+s
}

function setup_song_events()
{
    $('li.song').bind('click', function(e){
        if(currTrack == e.target.id)
        {
            //console.log("i'm awake!", playerState);
            if(playerState in arrayToDict(['PLAYING', 'BUFFERING']))
                p.sendEvent("PLAY", false);
            else if(playerState in arrayToDict(['PAUSED', 'IDLE']))
                p.sendEvent("PLAY", true);
        }
        else
        {
            currTrack = e.target.id;
            clearClocks();
            p.sendEvent('ITEM', currTrack);
            p.sendEvent('PLAY', true);
        }
    });
}

function arrayToDict(a)
{
    var o = {};
    for(var i=0;i<a.length;i++)
    {
        o[a[i]]='';
    }
    return o;
}
