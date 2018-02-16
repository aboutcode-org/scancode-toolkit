/*  This file is part of the KDE project
    Copyright (C) 2006 Tim Beaulen <tbscope@gmail.com>
    Copyright (C) 2006-2007 Matthias Kretz <kretz@kde.org>

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.

    You should have received a copy of the GNU Library General Public License
    along with this library; see the file COPYING.LIB.  If not, write to
    the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
    Boston, MA 02110-1301, USA.

*/

#include "backend.h"
#include <phonon/experimental/backendinterface.h>
#include <phonon/pulsesupport.h>
#include "mediaobject.h"
#include "effect.h"
#include "events.h"
#include "audiooutput.h"
#include "audiodataoutput.h"
#include "nullsink.h"
#include "visualization.h"
#include "volumefadereffect.h"
#include "videodataoutput.h"
#include "videowidget.h"
#include "wirecall.h"
#include "xinethread.h"
#include "keepreference.h"
#include "sinknode.h"
#include "sourcenode.h"
#include "config-xine-widget.h"

#include <QtCore/QByteArray>
#include <QtCore/QThread>
#include <QtDBus/QDBusConnection>
#include <QtGui/QApplication>
#include <QtCore/QSet>
#include <QtCore/QVariant>
#include <QtCore/QtPlugin>
#include <QtCore/QSettings>

Q_EXPORT_PLUGIN2(phonon_xine, Phonon::Xine::Backend)

static Phonon::Xine::Backend *s_instance = 0;

namespace Phonon
{
namespace Xine
{

Backend *Backend::instance()
{
    Q_ASSERT(s_instance);
    return s_instance;
}

Backend::Backend(QObject *parent, const QVariantList &)
    : QObject(parent),
    m_inShutdown(false),
    m_debugMessages(!qgetenv("PHONON_XINE_DEBUG").isEmpty()),
    m_thread(0)
{
    // Initialise PulseAudio support
    PulseSupport *pulse = PulseSupport::getInstance();
    pulse->enable();
    connect(pulse, SIGNAL(objectDescriptionChanged(ObjectDescriptionType)), SLOT(emitObjectDescriptionChanged(ObjectDescriptionType)));

    Q_ASSERT(s_instance == 0);
    s_instance = this;

    m_xine.create();
    m_freeEngines << m_xine;

    setProperty("identifier",     QLatin1String("phonon_xine"));
    setProperty("backendName",    QLatin1String("Xine"));
    setProperty("backendComment", tr("Phonon Xine Backend"));
    setProperty("backendVersion", QLatin1String("0.1"));
    setProperty("backendIcon",    QLatin1String("phonon-xine"));
    setProperty("backendWebsite", QLatin1String("http://multimedia.kde.org/"));

    QSettings cg("kde.org", "Phonon-Xine");
    m_deinterlaceDVD = cg.value("Settings/deinterlaceDVD", true).toBool();
    m_deinterlaceVCD = cg.value("Settings/deinterlaceVCD", false).toBool();
    m_deinterlaceFile = cg.value("Settings/deinterlaceFile", false).toBool();
    m_deinterlaceMethod = cg.value("Settings/deinterlaceMethod", 0).toInt();

    signalTimer.setSingleShot(true);
    connect(&signalTimer, SIGNAL(timeout()), SLOT(emitAudioOutputDeviceChange()));
    QDBusConnection::sessionBus().registerObject("/internal/PhononXine", this, QDBusConnection::ExportScriptableSlots);

    debug() << Q_FUNC_INFO << "Using Xine version " << xine_get_version_string();
}

Backend::~Backend()
{
    m_inShutdown = true;

    if (!m_cleanupObjects.isEmpty()) {
        Q_ASSERT(m_thread);
        QCoreApplication::postEvent(m_thread, new Event(Event::Cleanup));
        while (!m_cleanupObjects.isEmpty()) {
            XineThread::msleep(200); // static QThread::msleep, but that one is protected and XineThread is our friend
        }
    }

    if (m_thread) {
        m_thread->quit();
        m_thread->wait();
        delete m_thread;
    }

    s_instance = 0;
    PulseSupport::shutdown();
}

XineEngine Backend::xineEngineForStream()
{
    XineEngine e;
    if (s_instance->m_freeEngines.isEmpty()) {
        e.create();
    } else {
        e = s_instance->m_freeEngines.takeLast();
    }
    s_instance->m_usedEngines << e;
    return e;
}

void Backend::returnXineEngine(const XineEngine &e)
{
    s_instance->m_usedEngines.removeAll(e);
    s_instance->m_freeEngines << e;
    if (s_instance->m_freeEngines.size() > 5) {
        s_instance->m_freeEngines.takeLast();
        s_instance->m_freeEngines.takeLast();
        s_instance->m_freeEngines.takeLast();
    }
}

QObject *Backend::createObject(BackendInterface::Class c, QObject *parent, const QList<QVariant> &args)
{
    switch (c) {
    case MediaObjectClass:
        return new MediaObject(parent);
    case VolumeFaderEffectClass:
        return new VolumeFaderEffect(parent);
    case AudioOutputClass:
        return new AudioOutput(parent);
    case AudioDataOutputClass:
        return new AudioDataOutput(parent);
    case VisualizationClass:
        return new Visualization(parent);
    case VideoDataOutputClass:
        return 0;
    case Phonon::Experimental::BackendInterface::VideoDataOutputClass:
        return new VideoDataOutput(parent);
    case EffectClass:
        {
            Q_ASSERT(args.size() == 1);
            debug() << Q_FUNC_INFO << "creating Effect(" << args[0];
            Effect *e = new Effect(args[0].toInt(), parent);
            if (e->isValid()) {
                return e;
            }
            delete e;
            return 0;
        }
    case VideoWidgetClass:
        {
#ifdef XINEWIDGET_FOUND 
            VideoWidget *vw = new VideoWidget(qobject_cast<QWidget *>(parent));
            if (vw->isValid()) {
                return vw;
            }
            delete vw;
#endif
            return 0;
        }
    }
    return 0;
}

QStringList Backend::availableMimeTypes() const
{
    if (m_supportedMimeTypes.isEmpty())
    {
        char *mimeTypes_c = xine_get_mime_types(m_xine);
        QString mimeTypes(mimeTypes_c);
        free(mimeTypes_c);
        QStringList lstMimeTypes = mimeTypes.split(";", QString::SkipEmptyParts);
        foreach (const QString &mimeType, lstMimeTypes) {
            m_supportedMimeTypes << mimeType.left(mimeType.indexOf(':')).trimmed();
        }
        if (m_supportedMimeTypes.contains("application/ogg")) {
            m_supportedMimeTypes << QLatin1String("audio/x-vorbis+ogg") << QLatin1String("application/ogg");
        }
    }

    return m_supportedMimeTypes;
}

QList<int> Backend::objectDescriptionIndexes(ObjectDescriptionType type) const
{
    QList<int> list;
    switch(type)
    {
    case Phonon::AudioOutputDeviceType:
        return Backend::audioOutputIndexes();
    case Phonon::AudioCaptureDeviceType:
        break;
/*
    case Phonon::VideoOutputDeviceType:
        {
            const char *const *outputPlugins = xine_list_video_output_plugins(m_xine);
            for (int i = 0; outputPlugins[i]; ++i)
                list << 40000 + i;
            break;
        }
    case Phonon::VideoCaptureDeviceType:
        list << 30000 << 30001;
        break;
    case Phonon::VisualizationType:
        break;
    case Phonon::AudioCodecType:
        break;
    case Phonon::VideoCodecType:
        break;
    case Phonon::ContainerFormatType:
        break;
        */
    case Phonon::EffectType:
        {
            const char *const *postPlugins = xine_list_post_plugins_typed(m_xine, XINE_POST_TYPE_AUDIO_FILTER);
            for (int i = 0; postPlugins[i]; ++i)
                list << 0x7F000000 + i;
            /*const char *const *postVPlugins = xine_list_post_plugins_typed(m_xine, XINE_POST_TYPE_VIDEO_FILTER);
            for (int i = 0; postVPlugins[i]; ++i) {
                list << 0x7E000000 + i;
            } */
        }
    case Phonon::AudioChannelType:
    case Phonon::SubtitleType:
        {
            ObjectDescriptionHash hash = Backend::objectDescriptions();
            ObjectDescriptionHash::iterator it = hash.find(type);
            if(it != hash.end())
                list = it.value().keys();
        }
        break;
    }
    return list;
}

QHash<QByteArray, QVariant> Backend::objectDescriptionProperties(ObjectDescriptionType type, int index) const
{
    //debug() << Q_FUNC_INFO << type << index;
    QHash<QByteArray, QVariant> ret;
    switch (type) {
    case Phonon::AudioOutputDeviceType:
        ret = Backend::audioOutputProperties(index);
        break;
    case Phonon::AudioCaptureDeviceType:
        break;
        /*
    case Phonon::VideoOutputDeviceType:
        {
            const char *const *outputPlugins = xine_list_video_output_plugins(m_xine);
            for (int i = 0; outputPlugins[i]; ++i) {
                if (40000 + i == index) {
                    ret.insert("name", QLatin1String(outputPlugins[i]));
                    ret.insert("description", "");
                    // description should be the result of the following call, but it crashes.
                    // It looks like libxine initializes the plugin even when we just want the description...
                    //QLatin1String(xine_get_video_driver_plugin_description(m_xine, outputPlugins[i])));
                    break;
                }
            }
        }
        break;
    case Phonon::VideoCaptureDeviceType:
        switch (index) {
        case 30000:
            ret.insert("name", "USB Webcam");
            ret.insert("description", "first description");
            break;
        case 30001:
            ret.insert("name", "DV");
            ret.insert("description", "second description");
            break;
        }
        break;
    case Phonon::VisualizationType:
        break;
    case Phonon::AudioCodecType:
        break;
    case Phonon::VideoCodecType:
        break;
    case Phonon::ContainerFormatType:
        break;
        */
    case Phonon::EffectType:
        {
            const char *const *postPlugins = xine_list_post_plugins_typed(m_xine, XINE_POST_TYPE_AUDIO_FILTER);
            for (int i = 0; postPlugins[i]; ++i) {
                if (0x7F000000 + i == index) {
                    ret.insert("name", QLatin1String(postPlugins[i]));
                    ret.insert("description", QLatin1String(xine_get_post_plugin_description(m_xine, postPlugins[i])));
                    break;
                }
            }
            /*const char *const *postVPlugins = xine_list_post_plugins_typed(m_xine, XINE_POST_TYPE_VIDEO_FILTER);
            for (int i = 0; postVPlugins[i]; ++i) {
                if (0x7E000000 + i == index) {
                    ret.insert("name", QLatin1String(postPlugins[i]));
                    break;
                }
            } */
        }
    case Phonon::AudioChannelType:
    case Phonon::SubtitleType:
        {
            ObjectDescriptionHash descriptionHash = Backend::objectDescriptions();
            ObjectDescriptionHash::iterator descIt = descriptionHash.find(type);
            if(descIt != descriptionHash.end())
            {
                ChannelIndexHash indexHash = descIt.value();
                ChannelIndexHash::iterator indexIt = indexHash.find(index);
                if(indexIt != indexHash.end())
                {
                    ret = indexIt.value();
                }
            }
        }
        break;
    }
    return ret;
}

bool Backend::startConnectionChange(QSet<QObject *> nodes)
{
    Q_UNUSED(nodes);
    // there's nothing we can do but hope the connection changes won't take too long so that buffers
    // would underrun. But we should be pretty safe the way xine works by not doing anything here.
    m_disconnections.clear();
    return true;
}

bool Backend::connectNodes(QObject *_source, QObject *_sink)
{
    debug() << Q_FUNC_INFO << _source << "->" << _sink;
    SourceNode *source = qobject_cast<SourceNode *>(_source);
    SinkNode *sink = qobject_cast<SinkNode *>(_sink);
    if (!source || !sink) {
        return false;
    }
    debug() << Q_FUNC_INFO << source->threadSafeObject().data() << "->" << sink->threadSafeObject().data();
    // what streams to connect - i.e. all both nodes support
    const MediaStreamTypes types = source->outputMediaStreamTypes() & sink->inputMediaStreamTypes();
    if (sink->source() != 0 || source->sinks().contains(sink)) {
        return false;
    }
    NullSink *nullSink = 0;
    foreach (SinkNode *otherSinks, source->sinks()) {
        if (otherSinks->inputMediaStreamTypes() & types) {
            if (nullSink) {
                qWarning() << "phonon-xine does not support splitting of audio or video streams into multiple outputs. The sink node is already connected to" << otherSinks->threadSafeObject().data();
                return false;
            } else {
                nullSink = dynamic_cast<NullSink *>(otherSinks);
                if (!nullSink) {
                    qWarning() << "phonon-xine does not support splitting of audio or video streams into multiple outputs. The sink node is already connected to" << otherSinks->threadSafeObject().data();
                    return false;
                }
            }
        }
    }
    if (nullSink) {
        m_disconnections << WireCall(source, nullSink);
        source->removeSink(nullSink);
        nullSink->unsetSource(source);
    }
    source->addSink(sink);
    sink->setSource(source);
    return true;
}

bool Backend::disconnectNodes(QObject *_source, QObject *_sink)
{
    debug() << Q_FUNC_INFO << _source << "XX" << _sink;
    SourceNode *source = qobject_cast<SourceNode *>(_source);
    SinkNode *sink = qobject_cast<SinkNode *>(_sink);
    if (!source || !sink) {
        return false;
    }
    debug() << Q_FUNC_INFO << source->threadSafeObject().data() << "XX" << sink->threadSafeObject().data();
    const MediaStreamTypes types = source->outputMediaStreamTypes() & sink->inputMediaStreamTypes();
    if (!source->sinks().contains(sink) || sink->source() != source) {
        return false;
    }
    m_disconnections << WireCall(source, sink);
    source->removeSink(sink);
    sink->unsetSource(source);
    return true;
}

bool Backend::endConnectionChange(QSet<QObject *> nodes)
{
    QList<WireCall> wireCallsUnordered;
    QList<WireCall> wireCalls;
    QList<QExplicitlySharedDataPointer<SharedData> > allXtObjects;
    KeepReference<> *keep = new KeepReference<>();

    // first we need to find all vertices of the subgraphs formed by the given nodes that are
    // source nodes but don't have a sink node connected and connect them to the NullSink, otherwise
    // disconnections won't work
    QSet<QObject *> nullSinks;
    foreach (QObject *q, nodes) {
        SourceNode *source = qobject_cast<SourceNode *>(q);
        if (source && source->sinks().isEmpty()) {
            SinkNode *sink = qobject_cast<SinkNode *>(q);
            if (!sink || (sink && sink->source())) {
                NullSink *nullsink = new NullSink(q);
                source->addSink(nullsink);
                nullsink->setSource(source);
                nullSinks << nullsink;
            }
        }
    }
    nodes += nullSinks;

    // Now that we know (by looking at the subgraph of nodes formed by the given nodes) what has to
    // be rewired we go over the nodes in order (from sink to source) and rewire them (all called
    // from the xine thread).
    foreach (QObject *q, nodes) {
        SourceNode *source = qobject_cast<SourceNode *>(q);
        if (source) {
            //keep->addObject(source->threadSafeObject());
            allXtObjects.append(QExplicitlySharedDataPointer<SharedData>(source->threadSafeObject().data()));
            foreach (SinkNode *sink, source->sinks()) {
                WireCall w(source, sink);
                if (wireCallsUnordered.contains(w)) {
                    Q_ASSERT(!wireCalls.contains(w));
                    wireCalls << w;
                } else {
                    wireCallsUnordered << w;
                }
            }
        }
        SinkNode *sink = qobject_cast<SinkNode *>(q);
        if (sink) {
            keep->addObject(sink->threadSafeObject().data());
            allXtObjects.append(QExplicitlySharedDataPointer<SharedData>(sink->threadSafeObject().data()));
            if (sink->source()) {
                WireCall w(sink->source(), sink);
                if (wireCallsUnordered.contains(w)) {
                    Q_ASSERT(!wireCalls.contains(w));
                    wireCalls << w;
                } else {
                    wireCallsUnordered << w;
                }
            }
            sink->findXineEngine();
        } else if (!source) {
            debug() << Q_FUNC_INFO << q << "is neither a source nor a sink";
        }
        ConnectNotificationInterface *connectNotify = qobject_cast<ConnectNotificationInterface *>(q);
        if (connectNotify) {
            // the object wants to know when the graph has changed
            connectNotify->graphChanged();
        }
    }
    if (!wireCalls.isEmpty()) {
        qSort(wireCalls);
        // we want to be safe and make sure that the execution of a WireCall has all objects still
        // alive that were used in this connection change
        QList<WireCall>::Iterator it = wireCalls.begin();
        const QList<WireCall>::Iterator end = wireCalls.end();
        for (; it != end; ++it) {
            it->addReferenceTo(allXtObjects);
        }
    }
    QCoreApplication::postEvent(XineThread::instance(), new RewireEvent(wireCalls, m_disconnections));
    m_disconnections.clear();
    keep->ready();
    return true;
}

void Backend::emitAudioOutputDeviceChange()
{
    debug() << Q_FUNC_INFO;
    emitObjectDescriptionChanged(AudioOutputDeviceType);
}

void Backend::emitObjectDescriptionChanged(ObjectDescriptionType type)
{
    emit objectDescriptionChanged(type);
}

bool Backend::deinterlaceDVD()
{
    return s_instance->m_deinterlaceDVD;
}

bool Backend::deinterlaceVCD()
{
    return s_instance->m_deinterlaceVCD;
}

bool Backend::deinterlaceFile()
{
    return s_instance->m_deinterlaceFile;
}

int Backend::deinterlaceMethod()
{
    return s_instance->m_deinterlaceMethod;
}

void Backend::setObjectDescriptionProperities(ObjectDescriptionType type, int index, const QHash<QByteArray, QVariant>& properities)
{
    s_instance->m_objectDescriptions[type][index] = properities;
}

QList<int> Backend::audioOutputIndexes()
{
    instance()->checkAudioOutputs();
    const Backend *const that = instance();
    debug() << Q_FUNC_INFO << that << that->m_audioOutputInfos.size();
    QList<int> list;
    for (int i = 0; i < that->m_audioOutputInfos.size(); ++i) {
        list << that->m_audioOutputInfos[i].index;
    }
    return list;
}

QHash<QByteArray, QVariant> Backend::audioOutputProperties(int audioDevice)
{
    QHash<QByteArray, QVariant> ret;
    if (audioDevice < 10000) {
        return ret;
    }
    instance()->checkAudioOutputs();
    const Backend *const that = instance();

    for (int i = 0; i < that->m_audioOutputInfos.size(); ++i) {
        if (that->m_audioOutputInfos[i].index == audioDevice) {
            ret.insert("name", that->m_audioOutputInfos[i].name);
            ret.insert("description", that->m_audioOutputInfos[i].description);

            const QString iconName = that->m_audioOutputInfos[i].icon;
            if (!iconName.isEmpty())
                ret.insert("icon", iconName);
            else
                ret.insert("icon", QLatin1String("audio-card"));
            ret.insert("available", that->m_audioOutputInfos[i].available);

            ret.insert("initialPreference", that->m_audioOutputInfos[i].initialPreference);
            ret.insert("isAdvanced", that->m_audioOutputInfos[i].isAdvanced);
            if (that->m_audioOutputInfos[i].isHardware) {
                ret.insert("isHardwareDevice", true);
            }

            return ret;
        }
    }
    ret.insert("name", QString());
    ret.insert("description", QString());
    ret.insert("available", false);
    ret.insert("initialPreference", 0);
    ret.insert("isAdvanced", false);
    return ret;
}

QByteArray Backend::audioDriverFor(int audioDevice)
{
    instance()->checkAudioOutputs();
    const Backend *const that = instance();
    for (int i = 0; i < that->m_audioOutputInfos.size(); ++i) {
        if (that->m_audioOutputInfos[i].index == audioDevice) {
            return that->m_audioOutputInfos[i].driver;
        }
    }
    return QByteArray();
}

void Backend::addAudioOutput(int index, int initialPreference, const QString &name, const QString &description,
        const QString &icon, const QByteArray &driver, bool isAdvanced, bool isHardware)
{
    AudioOutputInfo info(index, initialPreference, name, description, icon, driver);
    info.isAdvanced = isAdvanced;
    info.isHardware = isHardware;
    const int listIndex = m_audioOutputInfos.indexOf(info);
    if (listIndex == -1) {
        info.available = true;
        m_audioOutputInfos << info;
    } else {
        AudioOutputInfo &infoInList = m_audioOutputInfos[listIndex];
        if (infoInList.icon != icon || infoInList.initialPreference != initialPreference) {
            infoInList.icon = icon;
            infoInList.initialPreference = initialPreference;
        }
        infoInList.available = true;
    }
}

void Backend::checkAudioOutputs()
{
    if (m_audioOutputInfos.isEmpty()) {
        debug() << Q_FUNC_INFO << "isEmpty";
        int nextIndex = 10000;

        // This will list the audio drivers, not the actual devices.
        const char *const *outputPlugins = xine_list_audio_output_plugins(m_xine);

        PulseSupport *pulse = PulseSupport::getInstance();
        if (pulse->isActive()) {
            for (int i = 0; outputPlugins[i]; ++i) {
                if (0 == strcmp(outputPlugins[i], "pulseaudio")) {
                    // We've detected the pulseaudio output plugin. We're done.
                    return;
                }
            }

            // We cannot find the output plugin, so let the support class know.
            pulse->enable(false);
        }

        for (int i = 0; outputPlugins[i]; ++i) {
            debug() << Q_FUNC_INFO << "outputPlugin: " << outputPlugins[i];
            if (0 == strcmp(outputPlugins[i], "alsa")) {
                // we just list "default" for fallback when the platform plugin fails to list
                // devices
                addAudioOutput(nextIndex++, 12, tr("ALSA default output"),
                        tr("<html><p>The Platform Plugin failed. This is a fallback to use the "
                            "first ALSA device available.</p></html>", "This string is only shown "
                            "when the KDE runtime is broken. The technical term 'Platform Plugin' "
                            "might help users to find a solution, so it might make sense to leave "
                            "that term untranslated."),
                        /*icon name */"audio-card", outputPlugins[i], false, true);
            } else if (0 == strcmp(outputPlugins[i], "oss")) {
                // we just list /dev/dsp for fallback when the platform plugin fails to list
                // devices
                addAudioOutput(nextIndex++, 11, tr("OSS default output"),
                        tr("<html><p>The Platform Plugin failed. This is a fallback to use the "
                            "first OSS device available.</p></html>", "This string is only shown "
                            "when the KDE runtime is broken. The technical term 'Platform Plugin' "
                            "might help users to find a solution, so it might make sense to leave "
                            "that term untranslated."),
                        /*icon name */"audio-card", outputPlugins[i], false, true);
            } else if (0 == strcmp(outputPlugins[i], "none")
                    || 0 == strcmp(outputPlugins[i], "file")) {
                // ignore these drivers (hardware devices are listed by the KDE platform plugin)
            } else if (0 == strcmp(outputPlugins[i], "jack")) {
                addAudioOutput(nextIndex++, 9, tr("Jack Audio Connection Kit"),
                        tr("<html><p>JACK is a low-latency audio server. It can connect a number "
                            "of different applications to an audio device, as well as allowing "
                            "them to share audio between themselves.</p>"
                            "<p>JACK was designed from the ground up for professional audio "
                            "work, and its design focuses on two key areas: synchronous "
                            "execution of all clients, and low latency operation.</p></html>"),
                            /*icon name */"audio-backend-jack", outputPlugins[i]);
            } else if (0 == strcmp(outputPlugins[i], "arts")) {
                addAudioOutput(nextIndex++, -100, tr("aRts"),
                        tr("<html><p>aRts is the old sound server and media framework that was used "
                            "in KDE2 and KDE3. Its use is discouraged.</p></html>"),
                        /*icon name */"audio-backend-arts", outputPlugins[i]);
            } else if (0 == strcmp(outputPlugins[i], "pulseaudio")) {
                // Ignore this. We deal with it as a special case above.
            } else if (0 == strcmp(outputPlugins[i], "esd")) {
                addAudioOutput(nextIndex++, 8, tr("Esound (ESD)"),
                        xine_get_audio_driver_plugin_description(m_xine, outputPlugins[i]),
                        /*icon name */"audio-backend-esd", outputPlugins[i]);
            } else {
                addAudioOutput(nextIndex++, -20, outputPlugins[i],
                        xine_get_audio_driver_plugin_description(m_xine, outputPlugins[i]),
                        /*icon name */outputPlugins[i], outputPlugins[i]);
            }
        }

        qSort(m_audioOutputInfos);

        // now m_audioOutputInfos holds all devices this computer has ever seen
        foreach (const AudioOutputInfo &info, m_audioOutputInfos) {
            debug() << Q_FUNC_INFO << info.index << info.name << info.driver;
        }
    }
}

}}

#include "backend.moc"
