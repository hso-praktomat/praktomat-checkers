plugins {
    java
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.github.andrewoma.dexx:collection:0.7")
    implementation("org.junit.jupiter:junit-jupiter:5.12.0")
    implementation("junit:junit:4.13.2")
    implementation("org.junit.platform:junit-platform-launcher:1.12.0")
}

tasks.register<Copy>("getDeps") {
    val mainSource = sourceSets.main.get()
    from(mainSource.compileClasspath, mainSource.runtimeClasspath)
    into("runtime/")

    doFirst {
        delete("runtime")
        mkdir("runtime")
    }

    doLast {
        delete("runtime")
    }
}
