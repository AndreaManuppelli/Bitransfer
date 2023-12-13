
import { Component, OnInit } from '@angular/core';
import { Options } from 'ngx-qrcode-styling'; // Options for QR code styling
import { ServerService } from '../server.service'; // Service to interact with the backend/server
import { ActivatedRoute } from '@angular/router'; // Angular router module to get route parameters
import { BehaviorSubject, merge, Subject } from 'rxjs'; // RxJS reactive programming tools
import { filter, takeUntil, take } from 'rxjs/operators'; // RxJS operators

@Component({
  selector: 'app-payment',  // The CSS selector for the component's template
  templateUrl: './payment.component.html',  // Location of the component's template
  styleUrls: ['./payment.component.scss'],  // Location of the component's private CSS styles
})
export class PaymentComponent implements OnInit {
  public title: string = 'paywall-front-end';
  public qrCodeColor: string = getComputedStyle(document.documentElement).getPropertyValue('--surface-card').trim();
  public qrCodeBG: string = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim();
  public paymentId: string = "";
  public paymentData: any = {};
  public dataLoaded: boolean = false; // Indicates if data has been loaded
  public confirmed: boolean = false;
  private coinsRate: any = {};
  public configQr: Options = {};
  public amountRecived: number = 0;

  // Variables related to animations.
  public currentCard: 'card1' | 'card2' | 'none' = 'card1';
  public currentAnimation: 'none' | 'changeToCard2' | 'changeToCard1' = 'none';
  public animationInitiated: boolean = false;
  public isCard1Visible: boolean = true;

  // Observables for detecting payment status
  private paid_not_confirmed$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  private destroy$: Subject<void> = new Subject<void>(); // Used for unsubscribing from observables
  private intervalId: any; // To store the setInterval ID

  constructor(private server: ServerService, private route: ActivatedRoute) { }

  ngOnInit(): void {
    // Fetch the payment ID from route parameters
    this.route.params.subscribe(params => {
      this.paymentId = params['id'];
    });

    // Subscribe to changes in the payment detection observables
    merge(this.paid_not_confirmed$)
      .pipe(
        takeUntil(this.destroy$),
        filter(value => value === true),
        take(1)
      )
      .subscribe(() => {
        this.changeCard();
      });

    // Begin fetching data from the server
    this.startFetching();
  }

  // Method to fetch the Bitcoin price
  private fetchBtcPrice(): void {
    this.server.fetchBtcPrice().subscribe(response => {
      this.coinsRate = response;
    });
  }

  // Convert BTC amount to USD
  public convertBtcToUsd(btcValue: number): number {
    let usdValue = btcValue * this.coinsRate.btc;
    return parseFloat(usdValue.toFixed(2)); // Return converted value up to 2 decimal places
  }

  // Fetch payment data from the server
  private fetchData(): void {
    this.server.fetchData(this.paymentId).subscribe(response => {
      this.paymentData = response;

      if (this.paymentData.tx_confirmations === 3) {
        this.confirmed = true
      }

      // Update BehaviorSubject with new values
      this.paid_not_confirmed$.next(this.paymentData.paid_not_confirmed);

      // Configure the QR code with provided data
      this.configQr = {
        width: 200,
        height: 200,
        data: "bitcoin:" + this.paymentData.address + "?amount=" + this.paymentData.amount,
        image: "../assets/btc.png",
        margin: 5,
        dotsOptions: {
          color: this.qrCodeColor,
          type: "extra-rounded"
        },
        cornersSquareOptions: {
          type: "extra-rounded"
        },
        backgroundOptions: {
          color: this.qrCodeBG,
        },
        imageOptions: {
          crossOrigin: "anonymous",
          margin: 0
        }
      };

      this.dataLoaded = true; // Indicate that data has been loaded successfully
    });


  }

  // Start periodic fetching of data from the server
  private startFetching(): void {
    this.fetchData();
    this.fetchBtcPrice();
    this.intervalId = setInterval(() => {
      this.fetchData();
      this.fetchBtcPrice();
    }, 700);
  }

  // Stop periodic data fetching
  private stopFetching(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  // Logic to handle card change animations
  changeCard() {
    if (this.currentCard === 'card1') {
      this.animationInitiated = true;
        this.currentAnimation = 'changeToCard2';

        // Fai scomparire la card1
        setTimeout(() => {
            this.currentCard = 'none';

            // Show card2 after delay
            setTimeout(() => {
                this.currentCard = 'card2';
                this.currentAnimation = 'none';
            }, 50);  // Questo è solo un breve intervallo per permettere alla card di essere effettivamente nascosta prima dell'animazione di entrata.

        }, 800);

    } else {
        this.currentAnimation = 'changeToCard1';

        // Hide card2
        setTimeout(() => {
            this.currentCard = 'none';

            // Show card2 after delay
            setTimeout(() => {
                this.currentCard = 'card1';
                this.currentAnimation = 'none';
            }, 50);  // Small delay.

        }, 800); 
    }
  }


  public copyAmount(): void{
    navigator.clipboard.writeText(this.paymentData.amount);
  }

  public copyAddress(): void{
    navigator.clipboard.writeText(this.paymentData.address);
  }

  public redirectMerchantWebsite(): void {
    window.location.href = 'https://www.google.it';
  }
}




























