#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

/*! \brief Example function; adds two numbers
    \param i first number
    \param j second number
    \return i+j
*/
int add(int i, int j)
{
    return i + j;
}

/*! \brief Calculates a density field based on observations
    \param observations coordinates of the observations
    \param x_size size of the field in x-direction
    \param y_size size of the field in y-direction
    \param sigma_x sigma in x-direction
    \param sigma_y sigma in y-direction
    \return density field
*/
std::vector<std::vector<double>>
calc_field( std::vector<std::array<double, 2>> observations,
            int x_size,
            int y_size,
            double sigma_x,
            double sigma_y )
{
  std::vector<std::vector<double>> result(x_size, std::vector<double>(y_size, 0));
  for ( auto&& obs : observations )
  {
    int xmin = std::max( static_cast<int>( obs[0] - 3*sigma_x ), 0 );
    int xmax = std::min( static_cast<int>( obs[0] + 3*sigma_x ), x_size ); 
    int ymin = std::max( static_cast<int>( obs[1] - 3*sigma_y ), 0 ); 
    int ymax = std::min( static_cast<int>( obs[1] + 3*sigma_y ), y_size );
    const double sigma_x2 = sigma_x*sigma_x;
    const double sigma_y2 = sigma_y*sigma_y;
    for ( int x = xmin; x < xmax; ++x )
    {
      for ( int y = ymin; y < ymax; ++y )
      {
         double dx = x - obs[0];
         double dy = y - obs[1];
         result[x][y] += exp( -(dx*dx)/sigma_x2 - (dy*dy)/sigma_y2);
      }
    }
  }
  return result;
}

PYBIND11_MODULE(density, m)
{
    m.doc() = "pybind11 density plugin"; // optional module docstring
    m.def("add", &add, "A function which adds two numbers");
    m.def("calc_field", &calc_field, "A function which calculates a density field");
}
