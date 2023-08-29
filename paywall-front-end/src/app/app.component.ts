import { Component } from '@angular/core';
import { MoveDirection, ClickMode, HoverMode, OutMode, Engine, Container } from "tsparticles-engine";
import { loadFull } from "tsparticles";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  mobileScreen: boolean = false;

  id = "tsparticles";
  color = getComputedStyle(document.documentElement)
  .getPropertyValue('--bg-mask')
  .trim();
    /* Starting from 1.19.0 you can use a remote url (AJAX request) to a JSON with the configuration */
    particlesUrl = "http://foo.bar/particles.json";

    /* or the classic JavaScript object */
    particlesOptions = {
        background: {
            color: {
                value: this.color,
            },
        },
        fpsLimit: 120,
        interactivity: {
            events: {
                onClick: {
                    enable: true,
                    mode: ClickMode.trail,
                },
                onHover: {
                    enable: true,
                    mode: HoverMode.slow,
                },
                resize: true,
            },
            modes: {
                push: {
                    quantity: 4,
                },
                repulse: {
                    distance: 200,
                    duration: 0.4,
                },
            },
        },
        particles: {
            color: {
                value: "#ffffff",
            },
            links: {
                color: "#ffffff",
                distance: 150,
                enable: false,
                opacity: 0.5,
                width: 1,
            },
            collisions: {
                enable: true,
            },
            move: {
                direction: MoveDirection.none,
                enable: true,
                outModes: {
                    default: OutMode.bounce,
                },
                random: false,
                speed: 0.4,
                straight: false,
            },
            number: {
                density: {
                    enable: false,
                    area: 1000,
                },
                value: 30,
            },
            opacity: {
                value: 0.5,
            },
            shape: {
                type: "image",
                image: {
                  src:
                    "../assets/btc.png"
                }
            },
            size: {
                value: { min: 1, max: 30 },
            },
        },
        detectRetina: false,
    };

    ngOnInit() {
      this.mobileScreen = this.isMobileDevice();
    }

    isMobileDevice(): boolean {
      const userAgent = window.navigator.userAgent;
      return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
    }

    particlesLoaded(container: Container): void {
        console.log(container);
    }

    async particlesInit(engine: Engine): Promise<void> {
        

        // Starting from 1.19.0 you can add custom presets or shape here, using the current tsParticles instance (main)
        // this loads the tsparticles package bundle, it's the easiest method for getting everything ready
        // starting from v2 you can add only the features you need reducing the bundle size
        await loadFull(engine);
    }


}
