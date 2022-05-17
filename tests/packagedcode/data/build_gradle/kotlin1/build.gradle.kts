buildscript {

    repositories {
        google()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:3.3.0")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:1.3.11")
    }
}

allprojects {
    repositories {
        google()
        jcenter()
    }
}

