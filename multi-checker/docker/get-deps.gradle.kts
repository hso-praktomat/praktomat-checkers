plugins {
    java
}

repositories {
	mavenCentral()
}

dependencies {
	testImplementation("org.junit.jupiter:junit-jupiter:5.9.0")
	implementation("org.junit.jupiter:junit-jupiter:5.9.0")
}

tasks.register<Copy>("getDeps") {
    from(sourceSets.main.get().runtimeClasspath)
    into("runtime/")

    doFirst {
        delete("runtime")
        mkdir("runtime")
    }

    doLast {
        delete("runtime")
    }
}
