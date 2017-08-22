//  Fitting the signature rate via Oscillating Function.
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#define   DIM          5      // # parameters: p(t)

// Fit increase &  oscillating function.
double  fit_LS( int num, const double x[], const double y[], double par[]);
//  Calc Err
double  calc_err( int num, const double x[], const double y[], const double par[]);

// Fit Derivative of Gamma Function:
//    Initialize parameters: func_LM.c
void   init_par( int num, const double y[], double par[] );

//    Matrix & Vector in the Gauss-Newton method: func_LM.c
double calc_FH( int num, const double x[], const double y[], const double par[], double grad[], double H[]);

// Lovenberg-Marquadt method
double  solv_LM( int num, const double x[], const double y[], double *c_LM, double par[]);



int main(int argc, char *argv[])
{
  if( argc != 3 )
    {   printf("Usage:./a.out *f_in *f_out\n");  exit(1);  }

  FILE *f_in, *f_out;
  f_in  = fopen( argv[1], "r");
  if ( f_in == NULL)    {  printf("Cannot open $f_in\n");   exit(1);  }
  f_out = fopen( argv[2], "w");
  if ( f_in == NULL)    {  printf("Cannot open $f_out\n");   exit(1);  }

  int      i, num;     double  s_0;
  double   *dt, *r_sig;
  // Read parameters: Num. of Bins, Posted Time in a day
  fscanf( f_in, "%d  %lf", &num, &s_0);

  // Define Variables
  dt=    calloc( num, sizeof(double) );    // Time from Post
  r_sig= calloc( num, sizeof(double) );    // Signature Rate

  // Read: Time, Sginature Rate
  for (i=0; i<num; i++)
    {
      fscanf( f_in, "%lf  %lf", &dt[i], &r_sig[i]);
      dt[i] += 0.5;   // For Julia's data
    }

  double   err, par[DIM];
  err= fit_LS( num, dt, r_sig, par);

  // f_out: Parameter file  ( a, b, t_0, k, tau, err )
  fprintf ( f_out, "%.8f %.8f %f %f %f  %f\n",  par[0], par[1], par[2], par[3], par[4], err );

  free(dt);         free(r_sig);
  fclose(f_in);     fclose(f_out);     return 0;
}


// Fit nonlinear function: y[*] = F( x[*] )
double  fit_LS( int num, const double x[], const double y[], double par[])
{
  int      n_r= 0;
  double   c_LM = 0.001, eps= 1.0;
  init_par( num, y, par);

  // printf ( "# Init: ");    // Initial Value
  // for (k=0; k<DIM; k++)     printf ( "%f  ", par[k]);
  // printf ( "\n" );

  while ( eps> pow(0.1, 6)   )   // Nonlinear Least Square Method:
    {
      eps= solv_LM( num, x, y, &c_LM, par);     n_r++;
      if( n_r> pow(10, 4)  )
	{
	  // printf ( "# Error: No Convergence!!");
	  // for (k=0; k<DIM; k++)     printf ( "%f  ", par[k]);
	  // printf ( "\n" );
	  break;
	}
    }

  // printf ( "# Converged: ");   // Show parameters
  // for (k=0; k<DIM; k++)     printf ( "%f  ", par[k]);
  // printf ( "( Nr: %d) \n", n_r );

  return   calc_err( num, x, y, par);
}


// Calc. Error
double  calc_err( int num, const double x[], const double y[], const double par[])
{
  int   i;     double   err= 0, f_sin, f_dg;
  for (i=0; i<num; i++)
    {
      f_sin= par[0]+ par[1]* sin( M_PI* (x[i]+ par[2])/ 12 );
      f_dg=  pow( x[i], par[3] )* exp( (-1)* x[i]/ par[4] );
      err += pow( y[i]- f_sin* f_dg, 2 );
    }

  return  sqrt(err/ num );
}
